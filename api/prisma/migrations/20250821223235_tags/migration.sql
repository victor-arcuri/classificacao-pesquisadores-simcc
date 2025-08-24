-- CreateTable
CREATE TABLE "public"."researcher_tags" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(100),

    CONSTRAINT "researcher_tags_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."researcher_tags_on_researchers" (
    "researcher_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "assigned_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "researcher_tags_on_researchers_pkey" PRIMARY KEY ("researcher_id","tag_id")
);

-- AddForeignKey
ALTER TABLE "public"."researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."researcher_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;
