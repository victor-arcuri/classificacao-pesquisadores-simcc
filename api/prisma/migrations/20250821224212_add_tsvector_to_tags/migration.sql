CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TEXT SEARCH CONFIGURATION portuguese_unaccent (COPY = portuguese);

ALTER TEXT SEARCH CONFIGURATION portuguese_unaccent
ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, hword, hword_part, word WITH unaccent, portuguese_stem;

ALTER TABLE "public"."researcher_tags" ADD COLUMN "search_vector" tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('portuguese_unaccent', coalesce("name", '')), 'A')
) STORED;

CREATE INDEX researcher_tags_search_idx ON "public"."researcher_tags" USING GIN ("search_vector");