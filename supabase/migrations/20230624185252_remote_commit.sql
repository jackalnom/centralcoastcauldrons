
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pg_cron" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pg_net" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

CREATE EXTENSION IF NOT EXISTS "http" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_jsonschema" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "wrappers" WITH SCHEMA "extensions";

CREATE FUNCTION "public"."catalog"("api_url" "text") RETURNS "json"
    LANGUAGE "plpgsql"
    AS $$declare catalog json;

BEGIN
select *
into catalog
from http_get(api_url);

return catalog;
END$$;

ALTER FUNCTION "public"."catalog"("api_url" "text") OWNER TO "postgres";

CREATE FUNCTION "public"."catalog2"("api_url" "text") RETURNS "text"
    LANGUAGE "plpgsql"
    AS $$declare catalog text;

BEGIN
select *
into catalog
from http_get(api_url);

return catalog;
END$$;

ALTER FUNCTION "public"."catalog2"("api_url" "text") OWNER TO "postgres";

CREATE PROCEDURE "public"."catalog_for_shop"(IN "api_url" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text")
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  result http_response;
  url text;
  stack text;
  message text;
BEGIN
  url := api_url || 'catalog/';
  BEGIN
    PERFORM http_set_curlopt('CURLOPT_TIMEOUT_MS', '10001');
    result := http_get(url);
  EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
      error := (message || stack);
      return;
  END;

  INSERT INTO http_responses (url, status, content, shop_id, tick_id)
  VALUES (url, result.status, result.content, shop_id, tick_id);
  COMMIT;

  BEGIN
  insert into catalog_items (sku, name, quantity, potion_type, tick_id, shop_id, price)
    select sku, name, quantity, potion_type, tick_id, shop_id, price
    from
    json_populate_recordset(null::record, result.content::json)
    AS
    (
        sku text,
        name text,
        quantity smallint,
        price smallint,
        potion_type vector(3)
    );
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
      error := (message || stack);
      return;
  END;

  INSERT INTO public.jobs(shop_id, job_type, tick_id)
  VALUES(shop_id, 'PURCHASE_POTIONS', tick_id);
END;
$$;

ALTER PROCEDURE "public"."catalog_for_shop"(IN "api_url" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") OWNER TO "postgres";

CREATE FUNCTION "public"."execute_job"() RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$DECLARE
  job_cursor CURSOR FOR SELECT * FROM jobs WHERE success IS NULL LIMIT 1;
  job jobs%ROWTYPE;
  api_url text;
  stack text;
  message text;
BEGIN
  OPEN job_cursor;
  FETCH NEXT FROM job_cursor INTO job;
  CLOSE job_cursor;

  if not found then
     raise notice'No jobs to execute.';
  end if;

  api_url := (SELECT shops.api_url FROM shops WHERE id = job.shop_id);
  
  BEGIN
    CALL catalog_for_shop(api_url, job.shop_id, job.tick_id);

    UPDATE jobs SET success = TRUE WHERE id = job.id;
  EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
    UPDATE jobs SET success = FALSE, error = (message || stack) WHERE id = job.id;
  END;
END;$$;

ALTER FUNCTION "public"."execute_job"() OWNER TO "postgres";

CREATE FUNCTION "public"."fill_catalog"() RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$-- Declare necessary variables
DECLARE
  shop_record shops%ROWTYPE;
  tick_id int8;
BEGIN
  tick_id := (SELECT MAX(id) FROM ticks);

  -- Fetch records from the "shops" table
  FOR shop_record IN SELECT * FROM shops LOOP
    PERFORM fill_catalog_for_shop(shop_record.api_url, shop_record.id, tick_id);
  END LOOP;
END;$$;

ALTER FUNCTION "public"."fill_catalog"() OWNER TO "postgres";

CREATE FUNCTION "public"."fill_catalog_for_shop"("api_url" "text", "shop_id" bigint, "tick_id" bigint) RETURNS boolean
    LANGUAGE "plpgsql"
    AS $$DECLARE
  result http_response;
  url text;
BEGIN
  url := api_url || 'pyversion/';
  result := http_get(url);
  
  INSERT INTO http_responses (url, status, content, shop_id, tick_id)
  VALUES (url, result.status, result.content, shop_id, tick_id);
  
  insert into catalog_items (sku, name, quantity, description, tick_id, shop_id)
    select sku, name, quantity, description, tick_id, shop_id
    from
    json_populate_recordset(null::record, result.content::json)
    AS
    (
        sku text,
        name text,
        quantity smallint,
        description text
    );

  RETURN true;
END;$$;

ALTER FUNCTION "public"."fill_catalog_for_shop"("api_url" "text", "shop_id" bigint, "tick_id" bigint) OWNER TO "postgres";

CREATE PROCEDURE "public"."purchase_from_shop"(IN "api_url" "text", IN "api_key" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text")
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  result http_response;
  url text;
  stack text;
  message text;
  cart_id text;
  catalog_purchase catalog_items%ROWTYPE;
  gold int;
  amount_purchased int;
BEGIN
  SELECT * INTO catalog_purchase FROM catalog_items WHERE catalog_items.shop_id = purchase_from_shop.shop_id AND catalog_items.tick_id = purchase_from_shop.tick_id LIMIT 1;

  if not found then
    RAISE LOG 'no catalog found';
    return;
  end if;

  BEGIN
    PERFORM http_set_curlopt('CURLOPT_TIMEOUT_MS', '10001');

    SELECT json_extract_path(content::json, 'cart_id') INTO cart_id
      FROM http((
          'POST',
           api_url || 'carts/',
           ARRAY[http_header('access_token',api_key)],
           'application/json',
           ''
        )::http_request);
  EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
      error := (message || stack);
      return;
  END;

  BEGIN
    PERFORM http_set_curlopt('CURLOPT_TIMEOUT_MS', '10001');

    url := api_url || 'carts/' || cart_id || '/items/' || catalog_purchase.sku;

    PERFORM http((
          'PUT',
           url,
           ARRAY[http_header('access_token',api_key)],
           'application/json',
           '{"quantity": 1}'
        )::http_request);
  EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
      error := (message || stack);
      return;
  END;

  BEGIN
    PERFORM http_set_curlopt('CURLOPT_TIMEOUT_MS', '10001');

    PERFORM http((
          'POST',
           api_url || 'carts/' || cart_id || '/checkout',
           ARRAY[http_header('access_token',api_key)],
           'application/json',
           ''
        )::http_request);
  EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS stack = PG_EXCEPTION_CONTEXT, message = MESSAGE_TEXT;
      error := (message || stack);
      return;
  END;

  amount_purchased := catalog_purchase.quantity;

  insert into potion_ledger_items (shop_id, tick_id, quantity_changed, potion_type)
    values (shop_id, tick_id, -1 * amount_purchased, catalog_purchase.potion_type);
  gold := amount_purchased * catalog_purchase.price;

  insert into gold_ledger_items (shop_id, tick_id, gold_changed)
    values (shop_id, tick_id, gold);
END;
$$;

ALTER PROCEDURE "public"."purchase_from_shop"(IN "api_url" "text", IN "api_key" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") OWNER TO "postgres";

CREATE FUNCTION "public"."refresh_catalog"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  shop_record shops%ROWTYPE;
BEGIN
  -- Fetch records from the "shops" table
  FOR shop_record IN SELECT * FROM shops LOOP
    INSERT INTO public.jobs(shop_id, job_type, tick_id)
    VALUES(shop_record.id, 'REFRESH_CATALOG', new.id);
  END LOOP;

  return new;
END;
$$;

ALTER FUNCTION "public"."refresh_catalog"() OWNER TO "postgres";

CREATE PROCEDURE "public"."run_jobs"()
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  job jobs%ROWTYPE;
  shop shops%ROWTYPE;
  error_message text;
  counter integer := 0;
BEGIN
  while counter < 5 loop
    counter := counter + 1;
    raise log 'Counter %', counter;
    SELECT * INTO job FROM jobs WHERE success IS NULL ORDER BY created_at LIMIT 1;

    if not found then
      raise LOG 'No jobs to execute.';
      return;
    end if;

    SELECT * INTO shop FROM shops WHERE id = job.shop_id;

    error_message := null;

	  case 
		  when job.job_type = 'REFRESH_CATALOG' then
        CALL catalog_for_shop(shop.api_url, job.shop_id, job.tick_id, error_message);
      when job.job_type = 'PURCHASE_POTIONS' then
        CALL purchase_from_shop(shop.api_url, shop.api_key, job.shop_id, job.tick_id, error_message);
      else
        error_message := ('Unknown job type: ' || job.job_type);
    end case;  
    
    if error_message is null then
      UPDATE jobs SET success = TRUE WHERE id = job.id;
    else
      UPDATE jobs SET success = FALSE, error = error_message where id = job.id;
    end if;
    COMMIT;
  end loop;
END;
$$;

ALTER PROCEDURE "public"."run_jobs"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE "public"."barrel_ledger_items" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "shop_id" bigint NOT NULL,
    "tick_id" bigint NOT NULL,
    "liters_changed" smallint NOT NULL,
    "potion_type" "extensions"."vector"(3) NOT NULL
);

ALTER TABLE "public"."barrel_ledger_items" OWNER TO "postgres";

ALTER TABLE "public"."barrel_ledger_items" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."barrel_ledger_items_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."catalog_items" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "sku" "text",
    "name" "text",
    "quantity" smallint NOT NULL,
    "potion_type" "extensions"."vector"(3) NOT NULL,
    "price" smallint NOT NULL,
    "tick_id" bigint NOT NULL,
    "shop_id" bigint DEFAULT '1'::bigint NOT NULL
);

ALTER TABLE "public"."catalog_items" OWNER TO "postgres";

ALTER TABLE "public"."catalog_items" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."catalog_items_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."gold_ledger_items" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "shop_id" bigint NOT NULL,
    "tick_id" bigint NOT NULL,
    "gold_changed" smallint NOT NULL
);

ALTER TABLE "public"."gold_ledger_items" OWNER TO "postgres";

ALTER TABLE "public"."gold_ledger_items" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."gold_ledger_items_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."http_responses" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "status" integer,
    "content" "text",
    "url" "text" NOT NULL,
    "shop_id" bigint,
    "tick_id" bigint
);

ALTER TABLE "public"."http_responses" OWNER TO "postgres";

ALTER TABLE "public"."http_responses" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."http_responses_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."jobs" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "shop_id" bigint,
    "job_type" "text",
    "success" boolean,
    "error" "text",
    "tick_id" bigint DEFAULT '1'::bigint NOT NULL
);

ALTER TABLE "public"."jobs" OWNER TO "postgres";

ALTER TABLE "public"."jobs" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."jobs_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."potion_ledger_items" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "shop_id" bigint NOT NULL,
    "tick_id" bigint NOT NULL,
    "quantity_changed" smallint NOT NULL,
    "potion_type" "extensions"."vector"(3) NOT NULL
);

ALTER TABLE "public"."potion_ledger_items" OWNER TO "postgres";

ALTER TABLE "public"."potion_ledger_items" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."potion_ledger_items_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."shops" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "api_url" "text" NOT NULL,
    "shop_name" "text" NOT NULL,
    "student" "text",
    "api_key" "text",
    "section" "text"
);

ALTER TABLE "public"."shops" OWNER TO "postgres";

ALTER TABLE "public"."shops" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."shops_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE "public"."ticks" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);

ALTER TABLE "public"."ticks" OWNER TO "postgres";

ALTER TABLE "public"."ticks" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."ticks_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY "public"."barrel_ledger_items"
    ADD CONSTRAINT "barrel_ledger_items_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."gold_ledger_items"
    ADD CONSTRAINT "gold_ledger_items_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."http_responses"
    ADD CONSTRAINT "http_responses_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."potion_ledger_items"
    ADD CONSTRAINT "potion_ledger_items_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."shops"
    ADD CONSTRAINT "shops_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."ticks"
    ADD CONSTRAINT "ticks_pkey" PRIMARY KEY ("id");

CREATE TRIGGER "on_insert" AFTER INSERT ON "public"."ticks" FOR EACH ROW EXECUTE FUNCTION "public"."refresh_catalog"();

ALTER TABLE ONLY "public"."barrel_ledger_items"
    ADD CONSTRAINT "barrel_ledger_items_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."barrel_ledger_items"
    ADD CONSTRAINT "barrel_ledger_items_tick_id_fkey" FOREIGN KEY ("tick_id") REFERENCES "public"."ticks"("id");

ALTER TABLE ONLY "public"."catalog_items"
    ADD CONSTRAINT "catalog_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."catalog_items"
    ADD CONSTRAINT "catalog_tick_id_fkey" FOREIGN KEY ("tick_id") REFERENCES "public"."ticks"("id");

ALTER TABLE ONLY "public"."gold_ledger_items"
    ADD CONSTRAINT "gold_ledger_items_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."gold_ledger_items"
    ADD CONSTRAINT "gold_ledger_items_tick_id_fkey" FOREIGN KEY ("tick_id") REFERENCES "public"."ticks"("id");

ALTER TABLE ONLY "public"."http_responses"
    ADD CONSTRAINT "http_responses_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."http_responses"
    ADD CONSTRAINT "http_responses_tick_id_fkey" FOREIGN KEY ("tick_id") REFERENCES "public"."ticks"("id");

ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."potion_ledger_items"
    ADD CONSTRAINT "potion_ledger_items_shop_id_fkey" FOREIGN KEY ("shop_id") REFERENCES "public"."shops"("id");

ALTER TABLE ONLY "public"."potion_ledger_items"
    ADD CONSTRAINT "potion_ledger_items_tick_id_fkey" FOREIGN KEY ("tick_id") REFERENCES "public"."ticks"("id");

ALTER TABLE "public"."http_responses" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."jobs" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."shops" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."ticks" ENABLE ROW LEVEL SECURITY;

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON FUNCTION "public"."catalog"("api_url" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."catalog"("api_url" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."catalog"("api_url" "text") TO "service_role";

GRANT ALL ON FUNCTION "public"."catalog2"("api_url" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."catalog2"("api_url" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."catalog2"("api_url" "text") TO "service_role";

GRANT ALL ON PROCEDURE "public"."catalog_for_shop"(IN "api_url" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "anon";
GRANT ALL ON PROCEDURE "public"."catalog_for_shop"(IN "api_url" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "authenticated";
GRANT ALL ON PROCEDURE "public"."catalog_for_shop"(IN "api_url" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "service_role";

GRANT ALL ON FUNCTION "public"."execute_job"() TO "anon";
GRANT ALL ON FUNCTION "public"."execute_job"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."execute_job"() TO "service_role";

GRANT ALL ON FUNCTION "public"."fill_catalog"() TO "anon";
GRANT ALL ON FUNCTION "public"."fill_catalog"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."fill_catalog"() TO "service_role";

GRANT ALL ON FUNCTION "public"."fill_catalog_for_shop"("api_url" "text", "shop_id" bigint, "tick_id" bigint) TO "anon";
GRANT ALL ON FUNCTION "public"."fill_catalog_for_shop"("api_url" "text", "shop_id" bigint, "tick_id" bigint) TO "authenticated";
GRANT ALL ON FUNCTION "public"."fill_catalog_for_shop"("api_url" "text", "shop_id" bigint, "tick_id" bigint) TO "service_role";

GRANT ALL ON PROCEDURE "public"."purchase_from_shop"(IN "api_url" "text", IN "api_key" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "anon";
GRANT ALL ON PROCEDURE "public"."purchase_from_shop"(IN "api_url" "text", IN "api_key" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "authenticated";
GRANT ALL ON PROCEDURE "public"."purchase_from_shop"(IN "api_url" "text", IN "api_key" "text", IN "shop_id" bigint, IN "tick_id" bigint, OUT "error" "text") TO "service_role";

GRANT ALL ON FUNCTION "public"."refresh_catalog"() TO "anon";
GRANT ALL ON FUNCTION "public"."refresh_catalog"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."refresh_catalog"() TO "service_role";

GRANT ALL ON PROCEDURE "public"."run_jobs"() TO "anon";
GRANT ALL ON PROCEDURE "public"."run_jobs"() TO "authenticated";
GRANT ALL ON PROCEDURE "public"."run_jobs"() TO "service_role";

GRANT ALL ON TABLE "public"."barrel_ledger_items" TO "anon";
GRANT ALL ON TABLE "public"."barrel_ledger_items" TO "authenticated";
GRANT ALL ON TABLE "public"."barrel_ledger_items" TO "service_role";

GRANT ALL ON SEQUENCE "public"."barrel_ledger_items_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."barrel_ledger_items_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."barrel_ledger_items_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."catalog_items" TO "anon";
GRANT ALL ON TABLE "public"."catalog_items" TO "authenticated";
GRANT ALL ON TABLE "public"."catalog_items" TO "service_role";

GRANT ALL ON SEQUENCE "public"."catalog_items_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."catalog_items_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."catalog_items_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."gold_ledger_items" TO "anon";
GRANT ALL ON TABLE "public"."gold_ledger_items" TO "authenticated";
GRANT ALL ON TABLE "public"."gold_ledger_items" TO "service_role";

GRANT ALL ON SEQUENCE "public"."gold_ledger_items_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."gold_ledger_items_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."gold_ledger_items_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."http_responses" TO "anon";
GRANT ALL ON TABLE "public"."http_responses" TO "authenticated";
GRANT ALL ON TABLE "public"."http_responses" TO "service_role";

GRANT ALL ON SEQUENCE "public"."http_responses_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."http_responses_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."http_responses_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."jobs" TO "anon";
GRANT ALL ON TABLE "public"."jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs" TO "service_role";

GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."jobs_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."potion_ledger_items" TO "anon";
GRANT ALL ON TABLE "public"."potion_ledger_items" TO "authenticated";
GRANT ALL ON TABLE "public"."potion_ledger_items" TO "service_role";

GRANT ALL ON SEQUENCE "public"."potion_ledger_items_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."potion_ledger_items_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."potion_ledger_items_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."shops" TO "anon";
GRANT ALL ON TABLE "public"."shops" TO "authenticated";
GRANT ALL ON TABLE "public"."shops" TO "service_role";

GRANT ALL ON SEQUENCE "public"."shops_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."shops_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."shops_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."ticks" TO "anon";
GRANT ALL ON TABLE "public"."ticks" TO "authenticated";
GRANT ALL ON TABLE "public"."ticks" TO "service_role";

GRANT ALL ON SEQUENCE "public"."ticks_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."ticks_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."ticks_id_seq" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
