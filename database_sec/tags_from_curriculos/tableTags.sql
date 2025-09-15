CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- CreateTable
CREATE TABLE IF NOT EXISTS "researcher_tags" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_in" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(100) NOT NULL UNIQUE,

    CONSTRAINT "researcher_tags_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "researcher_tags_on_researchers" (
    "researcher_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "assigned_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "researcher_tags_on_researchers_pkey" PRIMARY KEY ("researcher_id","tag_id")
);

-- AddForeignKey
ALTER TABLE "researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "curriculos"("id_pesquisador") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "researcher_tags_on_researchers" ADD CONSTRAINT "researcher_tags_on_researchers_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "researcher_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- Função que atualiza automaticamente a coluna updated_in em updates
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_in = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
