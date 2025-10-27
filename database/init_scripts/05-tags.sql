CREATE TABLE "public"."researcher_tags" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "embedding" vector(1536),
    "parent_tag" UUID DEFAULT NULL,

    CONSTRAINT "researcher_tags_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "public"."researcher_tags_on_researchers" (
    "researcher_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "assigned_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "researcher_tags_on_researchers_pkey" PRIMARY KEY ("researcher_id","tag_id")
);

ALTER TABLE "public"."researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "public"."researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."researcher_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp ON researcher_tags;
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON researcher_tags
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();