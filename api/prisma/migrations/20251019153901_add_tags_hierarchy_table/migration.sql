-- CreateTable
CREATE TABLE "public"."tags_hierarchy" (
    "tag_id" UUID NOT NULL,
    "parent_tag_id" UUID NOT NULL,

    CONSTRAINT "tags_hierarchy_pkey" PRIMARY KEY ("tag_id","parent_tag_id")
);

-- AddForeignKey
ALTER TABLE "public"."tags_hierarchy" ADD CONSTRAINT "tags_hierarchy_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."researcher_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."tags_hierarchy" ADD CONSTRAINT "tags_hierarchy_parent_tag_id_fkey" FOREIGN KEY ("parent_tag_id") REFERENCES "public"."researcher_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;
