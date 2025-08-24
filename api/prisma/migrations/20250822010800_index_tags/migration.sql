-- CreateIndex
CREATE INDEX "researcher_tags_name_idx" ON "public"."researcher_tags" USING GIN ("name" gin_trgm_ops);
