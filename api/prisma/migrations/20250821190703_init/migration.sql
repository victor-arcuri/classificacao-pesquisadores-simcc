CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE EXTENSION IF NOT EXISTS vector;

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "admin";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "admin_ufmg";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "embeddings";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "logs";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "ufmg";

-- CreateEnum
CREATE TYPE "public"."bibliographic_production_type_enum" AS ENUM ('BOOK', 'BOOK_CHAPTER', 'ARTICLE', 'WORK_IN_EVENT', 'TEXT_IN_NEWSPAPER_MAGAZINE');

-- CreateEnum
CREATE TYPE "public"."classification_class" AS ENUM ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'E+', 'E');

-- CreateEnum
CREATE TYPE "public"."relationship" AS ENUM ('COLABORADOR', 'PERMANENTE');

-- CreateEnum
CREATE TYPE "public"."routine_type" AS ENUM ('SOAP_LATTES', 'HOP', 'POPULATION', 'PRODUCTION', 'LATTES_10', 'IND_PROD', 'POG', 'OPEN_ALEX', 'SEARCH_TERM');

-- CreateTable
CREATE TABLE "admin"."feedback" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "rating" INTEGER NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "feedback_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin"."graduate_program" (
    "graduate_program_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "code" VARCHAR(100),
    "name" VARCHAR(100) NOT NULL,
    "area" VARCHAR(100) NOT NULL,
    "modality" VARCHAR(100) NOT NULL,
    "type" VARCHAR(100),
    "rating" VARCHAR(5),
    "institution_id" UUID NOT NULL,
    "state" VARCHAR(4) DEFAULT 'BA',
    "city" VARCHAR(100) DEFAULT 'Salvador',
    "region" VARCHAR(100) DEFAULT 'Nordeste',
    "url_image" VARCHAR(200),
    "acronym" VARCHAR(100),
    "description" TEXT,
    "visible" BOOLEAN DEFAULT false,
    "site" TEXT,
    "menagers" TEXT[],
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_pkey" PRIMARY KEY ("graduate_program_id")
);

-- CreateTable
CREATE TABLE "admin"."graduate_program_researcher" (
    "graduate_program_id" UUID NOT NULL,
    "researcher_id" UUID NOT NULL,
    "year" INTEGER[],
    "type_" "public"."relationship",
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_researcher_pkey" PRIMARY KEY ("graduate_program_id","researcher_id")
);

-- CreateTable
CREATE TABLE "admin"."graduate_program_student" (
    "graduate_program_id" UUID NOT NULL,
    "researcher_id" UUID NOT NULL,
    "year" INTEGER[],
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_student_pkey" PRIMARY KEY ("graduate_program_id","researcher_id","year")
);

-- CreateTable
CREATE TABLE "admin"."institution" (
    "institution_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "acronym" VARCHAR(50),
    "lattes_id" CHAR(16),
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "institution_pkey" PRIMARY KEY ("institution_id")
);

-- CreateTable
CREATE TABLE "admin"."newsletter_subscribers" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "email" VARCHAR(255) NOT NULL,
    "subscribed_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "newsletter_subscribers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin"."permission" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "role_id" UUID NOT NULL,
    "permission" VARCHAR(255) NOT NULL,

    CONSTRAINT "permission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin"."researcher" (
    "researcher_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(150) NOT NULL,
    "lattes_id" VARCHAR(20),
    "extra_field" VARCHAR(255),
    "status" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "researcher_pkey" PRIMARY KEY ("researcher_id")
);

-- CreateTable
CREATE TABLE "admin"."researcher_institution" (
    "researcher_institution_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "institution_id" UUID NOT NULL,
    "start_date" DATE DEFAULT CURRENT_DATE,
    "end_date" DATE,
    "is_current" BOOLEAN DEFAULT true,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "researcher_institution_pkey" PRIMARY KEY ("researcher_institution_id")
);

-- CreateTable
CREATE TABLE "admin"."roles" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "role" VARCHAR(255) NOT NULL,

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin"."users" (
    "user_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "display_name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "uid" VARCHAR(255) NOT NULL,
    "photo_url" TEXT,
    "lattes_id" VARCHAR(255),
    "institution_id" UUID,
    "provider" VARCHAR(255),
    "linkedin" VARCHAR(255),
    "verify" BOOLEAN DEFAULT false,
    "shib_id" VARCHAR(255),
    "shib_code" VARCHAR(255),
    "birth_date" VARCHAR(10),
    "course_level" VARCHAR(255),
    "first_name" VARCHAR(255),
    "registration" VARCHAR(255),
    "gender" VARCHAR(50),
    "last_name" VARCHAR(255),
    "email_status" VARCHAR(50),
    "visible_email" BOOLEAN,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "admin"."users_roles" (
    "role_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,

    CONSTRAINT "users_roles_pkey" PRIMARY KEY ("role_id","user_id")
);

-- CreateTable
CREATE TABLE "admin"."weights" (
    "institution_id" UUID NOT NULL,
    "a1" DECIMAL(20,3),
    "a2" DECIMAL(20,3),
    "a3" DECIMAL(20,3),
    "a4" DECIMAL(20,3),
    "b1" DECIMAL(20,3),
    "b2" DECIMAL(20,3),
    "b3" DECIMAL(20,3),
    "b4" DECIMAL(20,3),
    "c" DECIMAL(20,3),
    "sq" DECIMAL(20,3),
    "book" DECIMAL(20,3),
    "book_chapter" DECIMAL(20,3),
    "software" VARCHAR,
    "patent_granted" VARCHAR,
    "patent_not_granted" VARCHAR,
    "report" VARCHAR,
    "f1" DECIMAL(20,3) DEFAULT 0,
    "f2" DECIMAL(20,3) DEFAULT 0,
    "f3" DECIMAL(20,3) DEFAULT 0,
    "f4" DECIMAL(20,3) DEFAULT 0,
    "f5" DECIMAL(20,3) DEFAULT 0,

    CONSTRAINT "weights_pkey" PRIMARY KEY ("institution_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."department" (
    "dep_id" VARCHAR(20) NOT NULL,
    "org_cod" VARCHAR(3),
    "dep_nom" VARCHAR(100),
    "dep_des" TEXT,
    "dep_email" VARCHAR(100),
    "dep_site" VARCHAR(100),
    "dep_sigla" VARCHAR(30),
    "dep_tel" VARCHAR(20),
    "img_data" BYTEA,

    CONSTRAINT "department_pkey" PRIMARY KEY ("dep_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."department_researcher" (
    "dep_id" VARCHAR(20) NOT NULL,
    "researcher_id" UUID NOT NULL,

    CONSTRAINT "department_researcher_pkey" PRIMARY KEY ("dep_id","researcher_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."department_technician" (
    "dep_id" VARCHAR(20) NOT NULL,
    "technician_id" UUID NOT NULL,

    CONSTRAINT "department_technician_pkey" PRIMARY KEY ("dep_id","technician_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."disciplines" (
    "discipline_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "dep_id" VARCHAR(20),
    "semester" VARCHAR(20),
    "department" VARCHAR(255),
    "academic_activity_code" VARCHAR(255),
    "academic_activity_name" VARCHAR(255),
    "academic_activity_ch" VARCHAR(255),
    "demanding_courses" VARCHAR(255),
    "oft" VARCHAR(50),
    "available_slots" VARCHAR(50),
    "occupied_slots" VARCHAR(50),
    "percent_occupied_slots" VARCHAR(50),
    "schedule" VARCHAR(255),
    "language" VARCHAR(50),
    "researcher_id" UUID[],
    "researcher_name" VARCHAR[],
    "status" VARCHAR(50),
    "workload" VARCHAR[],

    CONSTRAINT "disciplines_pkey" PRIMARY KEY ("discipline_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."researcher" (
    "researcher_id" UUID NOT NULL,
    "full_name" VARCHAR(255),
    "gender" VARCHAR(255),
    "status_code" VARCHAR(255),
    "work_regime" VARCHAR(255),
    "job_class" CHAR(25),
    "job_title" VARCHAR(255),
    "job_rank" VARCHAR(255),
    "job_reference_code" VARCHAR(255),
    "academic_degree" VARCHAR(255),
    "organization_entry_date" DATE,
    "last_promotion_date" DATE,
    "employment_status_description" VARCHAR(255),
    "department_name" VARCHAR(255),
    "career_category" VARCHAR(255),
    "academic_unit" VARCHAR(255),
    "unit_code" VARCHAR(255),
    "function_code" VARCHAR(255),
    "position_code" VARCHAR(255),
    "leadership_start_date" DATE,
    "leadership_end_date" DATE,
    "current_function_name" VARCHAR(255),
    "function_location" VARCHAR(255),
    "registration_number" VARCHAR(200),
    "ufmg_registration_number" VARCHAR(200),
    "semester_reference" VARCHAR(6),

    CONSTRAINT "researcher_pkey" PRIMARY KEY ("researcher_id")
);

-- CreateTable
CREATE TABLE "admin_ufmg"."technician" (
    "technician_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "full_name" VARCHAR(255),
    "gender" VARCHAR(255),
    "status_code" VARCHAR(255),
    "work_regime" VARCHAR(255),
    "job_class" CHAR(25),
    "job_title" VARCHAR(255),
    "job_rank" VARCHAR(255),
    "job_reference_code" VARCHAR(255),
    "academic_degree" VARCHAR(255),
    "organization_entry_date" DATE,
    "last_promotion_date" DATE,
    "employment_status_description" VARCHAR(255),
    "department_name" VARCHAR(255),
    "career_category" VARCHAR(255),
    "academic_unit" VARCHAR(255),
    "unit_code" VARCHAR(255),
    "function_code" VARCHAR(255),
    "position_code" VARCHAR(255),
    "leadership_start_date" DATE,
    "leadership_end_date" DATE,
    "current_function_name" VARCHAR(255),
    "function_location" VARCHAR(255),
    "registration_number" VARCHAR(255),
    "ufmg_registration_number" VARCHAR(255),
    "semester_reference" VARCHAR(6),

    CONSTRAINT "technician_pkey" PRIMARY KEY ("technician_id")
);

-- CreateTable
CREATE TABLE "embeddings"."abstract" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "abstract_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."article" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "article_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."article_abstract" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "article_abstract_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."book" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "book_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."event" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "event_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."patent" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "reference_id" UUID,
    "embeddings" vector,
    "price" DECIMAL(20,18),

    CONSTRAINT "patent_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "logs"."researcher_routine" (
    "researcher_id" UUID NOT NULL,
    "type" "public"."routine_type" NOT NULL,
    "error" BOOLEAN DEFAULT false,
    "detail" TEXT,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "logs"."routine" (
    "type" "public"."routine_type" NOT NULL,
    "error" BOOLEAN DEFAULT false,
    "detail" TEXT,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "public"."area_expertise" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "great_area_expertise_id" UUID,

    CONSTRAINT "PK_44d189c8477ad880b9ec101d453" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."area_specialty" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "sub_area_expertise_id" UUID NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "pk_id_area_specialty" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."artistic_production" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "title" TEXT NOT NULL,
    "year" INTEGER,

    CONSTRAINT "artistic_production_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."bibliographic_production" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "title" VARCHAR(500) NOT NULL,
    "title_en" VARCHAR(500),
    "type" "public"."bibliographic_production_type_enum" NOT NULL,
    "doi" VARCHAR,
    "nature" VARCHAR(50),
    "year" CHAR(4),
    "country_id" UUID,
    "language" CHAR(2),
    "means_divulgation" VARCHAR(20),
    "homepage" VARCHAR,
    "relevance" BOOLEAN NOT NULL DEFAULT false,
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "scientific_divulgation" BOOLEAN DEFAULT false,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "researcher_id" UUID,
    "authors" VARCHAR(1000),
    "year_" INTEGER,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "PK_9c61219aee0513e9a1cf707a41a" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."bibliographic_production_article" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "bibliographic_production_id" UUID NOT NULL,
    "periodical_magazine_id" UUID NOT NULL,
    "volume" VARCHAR(30),
    "fascicle" VARCHAR(30),
    "series" VARCHAR(30),
    "start_page" VARCHAR(30),
    "end_page" VARCHAR(30),
    "place_publication" VARCHAR,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "periodical_magazine_name" VARCHAR(600),
    "issn" VARCHAR(20),
    "qualis" VARCHAR(8) DEFAULT 'SQ',
    "jcr" VARCHAR(100),
    "jcr_link" VARCHAR(200),

    CONSTRAINT "PK_3a53ca9c0bd82c629e7a14ef0f4" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."bibliographic_production_book" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "bibliographic_production_id" UUID NOT NULL,
    "isbn" CHAR(13),
    "qtt_volume" VARCHAR(25),
    "qtt_pages" VARCHAR(25),
    "num_edition_revision" VARCHAR(25),
    "num_series" VARCHAR(25),
    "publishing_company" VARCHAR,
    "publishing_company_city" VARCHAR,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "PK_818a520edae9528a6d586485d18" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."bibliographic_production_book_chapter" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "bibliographic_production_id" UUID NOT NULL,
    "book_title" VARCHAR,
    "isbn" CHAR(13),
    "start_page" VARCHAR(25),
    "end_page" VARCHAR(25),
    "qtt_volume" VARCHAR(25),
    "organizers" VARCHAR(500),
    "num_edition_revision" VARCHAR(25),
    "num_series" VARCHAR(25),
    "publishing_company" VARCHAR,
    "publishing_company_city" VARCHAR,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "PK_ccc5964c28ffa1e316b8c0c821e" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."bibliographic_production_work_in_event" (
    "bibliographic_production_id" UUID NOT NULL,
    "event_classification" VARCHAR(100),
    "event_name" VARCHAR(600),
    "event_city" VARCHAR(255),
    "event_year" INTEGER,
    "proceedings_title" VARCHAR(600),
    "volume" VARCHAR(30),
    "issue" VARCHAR(30),
    "series" VARCHAR(100),
    "start_page" VARCHAR(30),
    "end_page" VARCHAR(30),
    "publisher_name" VARCHAR(255),
    "publisher_city" VARCHAR(255),
    "event_name_english" VARCHAR(600),
    "identifier_number" VARCHAR(100),
    "isbn" VARCHAR(20),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "pk_bibliographic_production_event_work" PRIMARY KEY ("bibliographic_production_id")
);

-- CreateTable
CREATE TABLE "public"."brand" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(400),
    "relevance" BOOLEAN NOT NULL DEFAULT false,
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "goal" VARCHAR(255),
    "nature" VARCHAR(100),
    "researcher_id" UUID,
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "brand_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."city" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "country_id" UUID NOT NULL,
    "state_id" UUID,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "PK_b222f51ce26f7e5ca86944a6739" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."country" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "name_pt" VARCHAR NOT NULL,
    "alpha_2_code" CHAR(2),
    "alpha_3_code" CHAR(3),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "PK_bf6e37c231c4f4ea56dcd887269" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."didactic_material" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "title" TEXT NOT NULL,
    "country" VARCHAR,
    "nature" VARCHAR,
    "description" TEXT,
    "year" INTEGER,

    CONSTRAINT "didactic_material_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."education" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "degree" VARCHAR(255) NOT NULL,
    "education_name" VARCHAR(255),
    "education_start" INTEGER,
    "education_end" INTEGER,
    "key_words" VARCHAR(255),
    "institution" VARCHAR(255),

    CONSTRAINT "pk_education" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."event_organization" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(500),
    "promoter_institution" VARCHAR(500),
    "nature" VARCHAR(30),
    "researcher_id" UUID,
    "local" VARCHAR(500),
    "duration_in_weeks" SMALLINT,
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "event_organization_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."foment" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID,
    "modality_code" VARCHAR(50),
    "modality_name" VARCHAR(255),
    "call_title" VARCHAR(255),
    "category_level_code" VARCHAR(50),
    "funding_program_name" VARCHAR(255),
    "institute_name" VARCHAR(255),
    "aid_quantity" INTEGER,
    "scholarship_quantity" INTEGER
);

-- CreateTable
CREATE TABLE "public"."graduate_program" (
    "graduate_program_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "code" VARCHAR(100),
    "name" VARCHAR(100) NOT NULL,
    "name_en" VARCHAR(100),
    "basic_area" VARCHAR(100),
    "cooperation_project" VARCHAR(100),
    "area" VARCHAR(100) NOT NULL,
    "modality" VARCHAR(100) NOT NULL,
    "type" VARCHAR(100),
    "rating" VARCHAR(5),
    "institution_id" UUID NOT NULL,
    "state" VARCHAR(4) DEFAULT 'BA',
    "city" VARCHAR(100) DEFAULT 'Salvador',
    "region" VARCHAR(100) DEFAULT 'Nordeste',
    "url_image" VARCHAR(200),
    "acronym" VARCHAR(100),
    "description" TEXT,
    "visible" BOOLEAN DEFAULT false,
    "site" TEXT,
    "coordinator" VARCHAR(100),
    "email" VARCHAR(100),
    "start" DATE,
    "phone" VARCHAR(20),
    "periodicity" VARCHAR(50),
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_pkey" PRIMARY KEY ("graduate_program_id")
);

-- CreateTable
CREATE TABLE "public"."graduate_program_ind_prod" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "graduate_program_id" UUID NOT NULL,
    "year" INTEGER NOT NULL,
    "ind_prod_article" DECIMAL(10,3),
    "ind_prod_book" DECIMAL(10,3),
    "ind_prod_book_chapter" DECIMAL(10,3),
    "ind_prod_software" DECIMAL(10,3),
    "ind_prod_report" DECIMAL(10,3),
    "ind_prod_granted_patent" DECIMAL(10,3),
    "ind_prod_not_granted_patent" DECIMAL(10,3),
    "ind_prod_guidance" DECIMAL(10,3)
);

-- CreateTable
CREATE TABLE "public"."graduate_program_researcher" (
    "graduate_program_id" UUID NOT NULL,
    "researcher_id" UUID NOT NULL,
    "year" INTEGER[],
    "type_" "public"."relationship",
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_researcher_pkey" PRIMARY KEY ("graduate_program_id","researcher_id")
);

-- CreateTable
CREATE TABLE "public"."graduate_program_student" (
    "graduate_program_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "year" INTEGER[],
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "graduate_program_student_pkey" PRIMARY KEY ("graduate_program_id","researcher_id","year")
);

-- CreateTable
CREATE TABLE "public"."great_area_expertise" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "pk_id_great_area_expertise" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."guidance" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "researcher_id" UUID,
    "title" VARCHAR(400),
    "nature" VARCHAR(255),
    "oriented" VARCHAR(255),
    "type" VARCHAR(255),
    "status" VARCHAR(100),
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "guidance_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."institution" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "acronym" VARCHAR(50),
    "description" VARCHAR(5000),
    "lattes_id" CHAR(12),
    "cnpj" CHAR(14),
    "image" VARCHAR,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,

    CONSTRAINT "PK_f60ee4ff0719b7df54830b39087" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."jcr" (
    "rank" VARCHAR,
    "journalname" VARCHAR,
    "jcryear" VARCHAR,
    "abbrjournal" VARCHAR,
    "issn" VARCHAR,
    "eissn" VARCHAR,
    "totalcites" VARCHAR,
    "totalarticles" VARCHAR,
    "citableitems" VARCHAR,
    "citedhalflife" VARCHAR,
    "citinghalflife" VARCHAR,
    "jif2019" DOUBLE PRECISION,
    "url_revista" VARCHAR
);

-- CreateTable
CREATE TABLE "public"."openalex_article" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "article_id" UUID NOT NULL,
    "article_institution" VARCHAR,
    "issn" VARCHAR,
    "authors_institution" VARCHAR,
    "abstract" TEXT,
    "authors" VARCHAR,
    "language" VARCHAR,
    "citations_count" SMALLINT,
    "pdf" VARCHAR,
    "landing_page_url" VARCHAR,
    "keywords" VARCHAR,

    CONSTRAINT "PK_FIXMEHELP" PRIMARY KEY ("article_id")
);

-- CreateTable
CREATE TABLE "public"."openalex_researcher" (
    "researcher_id" UUID,
    "h_index" INTEGER,
    "relevance_score" DOUBLE PRECISION,
    "works_count" INTEGER,
    "cited_by_count" INTEGER,
    "i10_index" INTEGER,
    "scopus" VARCHAR(255),
    "orcid" VARCHAR(255),
    "openalex" VARCHAR(255)
);

-- CreateTable
CREATE TABLE "public"."participation_events" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(500),
    "event_name" VARCHAR(500),
    "nature" VARCHAR(30),
    "form_participation" VARCHAR(30),
    "type_participation" VARCHAR(30),
    "researcher_id" UUID,
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "participation_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."patent" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(400),
    "category" VARCHAR(200),
    "relevance" BOOLEAN NOT NULL DEFAULT false,
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "development_year" VARCHAR(10),
    "details" VARCHAR(2500),
    "researcher_id" UUID,
    "grant_date" TIMESTAMP(6),
    "deposit_date" VARCHAR(255),
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "patent_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."periodical_magazine" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(600),
    "issn" VARCHAR(20),
    "qualis" VARCHAR(8),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "jcr" VARCHAR(100),
    "jcr_link" VARCHAR(200),

    CONSTRAINT "PK_35bb0df687d8879d763c1f3ae68" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."relevant_production" (
    "researcher_id" UUID NOT NULL,
    "production_id" UUID NOT NULL,
    "type" VARCHAR NOT NULL,
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "relevant_production_pkey" PRIMARY KEY ("researcher_id","production_id","type")
);

-- CreateTable
CREATE TABLE "public"."research_dictionary" (
    "research_dictionary_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "term" VARCHAR(255),
    "frequency" INTEGER DEFAULT 1,
    "type_" VARCHAR(30),

    CONSTRAINT "research_dictionary_pkey" PRIMARY KEY ("research_dictionary_id")
);

-- CreateTable
CREATE TABLE "public"."research_group" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(200),
    "institution" VARCHAR(200),
    "first_leader" VARCHAR(200),
    "first_leader_id" UUID,
    "second_leader" VARCHAR(200),
    "second_leader_id" UUID,
    "area" VARCHAR(200),
    "census" INTEGER,
    "start_of_collection" VARCHAR(200),
    "end_of_collection" VARCHAR(200),
    "group_identifier" VARCHAR(200),
    "year" INTEGER,
    "institution_name" VARCHAR(200),
    "category" VARCHAR(200)
);

-- CreateTable
CREATE TABLE "public"."research_lines" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "research_group_id" UUID,
    "title" TEXT,
    "objective" TEXT,
    "keyword" VARCHAR(510),
    "group_identifier" VARCHAR(510),
    "year" INTEGER,
    "predominant_major_area" VARCHAR(510),
    "predominant_area" VARCHAR(510)
);

-- CreateTable
CREATE TABLE "public"."research_lines_programs" (
    "graduate_program_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" TEXT NOT NULL,
    "area" VARCHAR(255) NOT NULL,
    "start_year" INTEGER,
    "end_year" INTEGER,

    CONSTRAINT "research_lines_programs_pkey" PRIMARY KEY ("graduate_program_id","name")
);

-- CreateTable
CREATE TABLE "public"."research_project" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "start_year" INTEGER,
    "end_year" INTEGER,
    "agency_code" VARCHAR(255),
    "agency_name" VARCHAR(255),
    "project_name" TEXT,
    "status" VARCHAR(255),
    "nature" VARCHAR(255),
    "number_undergraduates" INTEGER DEFAULT 0,
    "number_specialists" INTEGER DEFAULT 0,
    "number_academic_masters" INTEGER DEFAULT 0,
    "number_phd" INTEGER DEFAULT 0,
    "description" TEXT,

    CONSTRAINT "research_project_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."research_project_components" (
    "project_id" UUID NOT NULL,
    "name" VARCHAR(255),
    "lattes_id" VARCHAR(255),
    "citations" VARCHAR
);

-- CreateTable
CREATE TABLE "public"."research_project_foment" (
    "project_id" UUID NOT NULL,
    "agency_name" VARCHAR(255),
    "agency_code" VARCHAR(255),
    "nature" VARCHAR(255)
);

-- CreateTable
CREATE TABLE "public"."research_project_production" (
    "project_id" UUID NOT NULL,
    "title" TEXT,
    "type" VARCHAR(255)
);

-- CreateTable
CREATE TABLE "public"."research_report" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "researcher_id" UUID,
    "title" VARCHAR(400),
    "project_name" VARCHAR(255),
    "financing_institutionc" VARCHAR(255),
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "research_report_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."researcher" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "lattes_id" CHAR(16),
    "lattes_10_id" CHAR(10),
    "last_update" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "citations" VARCHAR,
    "orcid" CHAR(31),
    "abstract" VARCHAR(5000),
    "abstract_en" VARCHAR(5000),
    "other_information" VARCHAR(5000),
    "city_id" UUID,
    "country_id" UUID,
    "classification" "public"."classification_class" DEFAULT 'E',
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "qtt_publications" INTEGER,
    "institution_id" UUID,
    "graduate_program" VARCHAR(255),
    "graduation" VARCHAR(30),
    "update_abstract" BOOLEAN DEFAULT true,
    "docente" BOOLEAN NOT NULL DEFAULT false,
    "student" BOOLEAN NOT NULL DEFAULT false,
    "extra_field" VARCHAR(255),
    "status" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "abstract_ai" TEXT,

    CONSTRAINT "PK_7b53850398061862ebe70d4ce44" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."researcher_address" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "city" VARCHAR(50),
    "organ" VARCHAR(255),
    "unity" VARCHAR(255),
    "institution" VARCHAR(255),
    "public_place" VARCHAR(255),
    "district" VARCHAR(255),
    "cep" VARCHAR(255),
    "mailbox" VARCHAR(255),
    "fax" VARCHAR(20),
    "url_homepage" VARCHAR(300),
    "telephone" VARCHAR(20),
    "country" VARCHAR(100),
    "uf" VARCHAR(5),

    CONSTRAINT "PK_180e58d987170694c2c11424916" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."researcher_area_expertise" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "sub_area_expertise_id" UUID NOT NULL,
    "order" INTEGER,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),
    "area_expertise_id" UUID,
    "great_area_expertise_id" UUID,
    "area_specialty_id" UUID,

    CONSTRAINT "PK_35338c2e178fa10e7b30966a4fc" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."researcher_ind_prod" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "year" INTEGER NOT NULL,
    "ind_prod_article" DECIMAL(10,3),
    "ind_prod_book" DECIMAL(10,3),
    "ind_prod_book_chapter" DECIMAL(10,3),
    "ind_prod_software" DECIMAL(10,3),
    "ind_prod_report" DECIMAL(10,3),
    "ind_prod_granted_patent" DECIMAL(10,3),
    "ind_prod_not_granted_patent" DECIMAL(10,3),
    "ind_prod_guidance" DECIMAL(10,3),

    CONSTRAINT "PKRIndProd" PRIMARY KEY ("researcher_id","year")
);

-- CreateTable
CREATE TABLE "public"."researcher_production" (
    "researcher_production_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "articles" INTEGER,
    "book_chapters" INTEGER,
    "book" INTEGER,
    "work_in_event" INTEGER,
    "patent" INTEGER,
    "software" INTEGER,
    "brand" INTEGER,
    "great_area" TEXT,
    "great_area_" TEXT[],
    "area_specialty" TEXT,
    "city" VARCHAR(100),
    "organ" VARCHAR(100),

    CONSTRAINT "researcher_production_pkey" PRIMARY KEY ("researcher_production_id")
);

-- CreateTable
CREATE TABLE "public"."researcher_professional_experience" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "enterprise" VARCHAR(255),
    "start_year" INTEGER,
    "end_year" INTEGER,
    "employment_type" VARCHAR(255),
    "other_employment_type" VARCHAR(255),
    "functional_classification" VARCHAR(255),
    "other_functional_classification" VARCHAR(255),
    "workload_hours_weekly" VARCHAR(255),
    "exclusive_dedication" BOOLEAN,
    "additional_info" TEXT,

    CONSTRAINT "researcher_professional_experience_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."software" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR,
    "platform" VARCHAR,
    "goal" VARCHAR,
    "relevance" BOOLEAN NOT NULL DEFAULT false,
    "has_image" BOOLEAN NOT NULL DEFAULT false,
    "environment" VARCHAR,
    "availability" VARCHAR,
    "financing_institutionc" VARCHAR,
    "researcher_id" UUID,
    "year" SMALLINT,
    "is_new" BOOLEAN DEFAULT true,

    CONSTRAINT "software_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."state" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "abbreviation" CHAR(2),
    "country_id" UUID NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "PK_549ffd046ebab1336c3a8030a12" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."sub_area_expertise" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR NOT NULL,
    "area_expertise_id" UUID NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6),
    "deleted_at" TIMESTAMP(6),

    CONSTRAINT "pk_id_sub_area_expertise" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."technical_work" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "country" VARCHAR,
    "title" TEXT NOT NULL,
    "nature" VARCHAR,
    "funding_institution" VARCHAR,
    "duration" INTEGER,
    "year" INTEGER,

    CONSTRAINT "technical_work_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."technical_work_presentation" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "country" VARCHAR,
    "title" TEXT NOT NULL,
    "nature" VARCHAR,
    "year" INTEGER,
    "event_name" VARCHAR,
    "promoting_institution" VARCHAR,

    CONSTRAINT "technical_work_presentation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."technical_work_program" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "country" VARCHAR,
    "title" TEXT NOT NULL,
    "nature" VARCHAR,
    "year" INTEGER,
    "theme" VARCHAR,

    CONSTRAINT "technical_work_program_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."technological_product" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "researcher_id" UUID NOT NULL,
    "country" VARCHAR,
    "title" TEXT NOT NULL,
    "nature" VARCHAR,
    "type" VARCHAR,
    "year" INTEGER,

    CONSTRAINT "technological_product_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ufmg"."departament" (
    "dep_id" VARCHAR(255) NOT NULL,
    "org_cod" VARCHAR(255),
    "dep_nom" VARCHAR(255),
    "dep_des" TEXT,
    "dep_email" VARCHAR(255),
    "dep_site" TEXT,
    "dep_sigla" VARCHAR(255),
    "dep_tel" VARCHAR(255),
    "img_data" BYTEA,

    CONSTRAINT "departament_pkey" PRIMARY KEY ("dep_id")
);

-- CreateTable
CREATE TABLE "ufmg"."departament_researcher" (
    "dep_id" VARCHAR(20) NOT NULL,
    "researcher_id" UUID NOT NULL,

    CONSTRAINT "departament_researcher_pkey" PRIMARY KEY ("dep_id","researcher_id")
);

-- CreateTable
CREATE TABLE "ufmg"."departament_technician" (
    "dep_id" VARCHAR(255) NOT NULL,
    "technician_id" UUID NOT NULL,

    CONSTRAINT "departament_technician_pkey" PRIMARY KEY ("dep_id","technician_id")
);

-- CreateTable
CREATE TABLE "ufmg"."mandate" (
    "member" VARCHAR(255),
    "departament" VARCHAR(255),
    "mandate" VARCHAR(255),
    "email" VARCHAR(255),
    "phone" VARCHAR(255)
);

-- CreateTable
CREATE TABLE "ufmg"."researcher" (
    "researcher_id" UUID NOT NULL,
    "full_name" VARCHAR(255),
    "gender" VARCHAR(255),
    "status_code" VARCHAR(255),
    "work_regime" VARCHAR(255),
    "job_class" CHAR(1),
    "job_title" VARCHAR(255),
    "job_rank" VARCHAR(255),
    "job_reference_code" VARCHAR(255),
    "academic_degree" VARCHAR(255),
    "organization_entry_date" DATE,
    "last_promotion_date" DATE,
    "employment_status_description" VARCHAR(255),
    "department_name" VARCHAR(255),
    "career_category" VARCHAR(255),
    "academic_unit" VARCHAR(255),
    "unit_code" VARCHAR(255),
    "function_code" VARCHAR(255),
    "position_code" VARCHAR(255),
    "leadership_start_date" DATE,
    "leadership_end_date" DATE,
    "current_function_name" VARCHAR(255),
    "function_location" VARCHAR(255),
    "registration_number" VARCHAR(200),
    "ufmg_registration_number" VARCHAR(200),
    "semester_reference" VARCHAR(6),

    CONSTRAINT "researcher_pkey" PRIMARY KEY ("researcher_id")
);

-- CreateTable
CREATE TABLE "ufmg"."researcher_data" (
    "nome" VARCHAR(255),
    "cpf" VARCHAR(14),
    "classe" INTEGER,
    "nivel" INTEGER,
    "inicio" TIMESTAMP(6),
    "fim" TIMESTAMP(6),
    "tempo_nivel" INTEGER,
    "tempo_acumulado" INTEGER,
    "arquivo" VARCHAR(255)
);

-- CreateTable
CREATE TABLE "ufmg"."technician" (
    "technician_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "full_name" VARCHAR(255),
    "gender" VARCHAR(255),
    "status_code" VARCHAR(255),
    "work_regime" VARCHAR(255),
    "job_class" CHAR(1),
    "job_title" VARCHAR(255),
    "job_rank" VARCHAR(255),
    "job_reference_code" VARCHAR(255),
    "academic_degree" VARCHAR(255),
    "organization_entry_date" DATE,
    "last_promotion_date" DATE,
    "employment_status_description" VARCHAR(255),
    "department_name" VARCHAR(255),
    "career_category" VARCHAR(255),
    "academic_unit" VARCHAR(255),
    "unit_code" VARCHAR(255),
    "function_code" VARCHAR(255),
    "position_code" VARCHAR(255),
    "leadership_start_date" DATE,
    "leadership_end_date" DATE,
    "current_function_name" VARCHAR(255),
    "function_location" VARCHAR(255),
    "registration_number" VARCHAR(255),
    "ufmg_registration_number" VARCHAR(255),
    "semester_reference" VARCHAR(6),

    CONSTRAINT "technician_pkey" PRIMARY KEY ("technician_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "graduate_program_code_key" ON "admin"."graduate_program"("code");

-- CreateIndex
CREATE UNIQUE INDEX "institution_acronym_key" ON "admin"."institution"("acronym");

-- CreateIndex
CREATE UNIQUE INDEX "newsletter_subscribers_email_key" ON "admin"."newsletter_subscribers"("email");

-- CreateIndex
CREATE UNIQUE INDEX "permission_role_id_permission_key" ON "admin"."permission"("role_id", "permission");

-- CreateIndex
CREATE UNIQUE INDEX "researcher_lattes_id_key" ON "admin"."researcher"("lattes_id");

-- CreateIndex
CREATE UNIQUE INDEX "researcher_institution_researcher_id_institution_id_is_curr_key" ON "admin"."researcher_institution"("researcher_id", "institution_id", "is_current");

-- CreateIndex
CREATE UNIQUE INDEX "roles_role_key" ON "admin"."roles"("role");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "admin"."users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_uid_key" ON "admin"."users"("uid");

-- CreateIndex
CREATE INDEX "area_expertise_name_idx" ON "public"."area_expertise" USING GIN ("name" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "bibliographic_production_title_idx" ON "public"."bibliographic_production" USING GIN ("title" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "brand_title_idx" ON "public"."brand" USING GIN ("title" gin_trgm_ops);

-- CreateIndex
CREATE UNIQUE INDEX "UQ_2c5aa339240c0c3ae97fcc9dc4c" ON "public"."country"("name");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_f7c67d6e048708bb13b14a0bc1a" ON "public"."country"("name_pt");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_69c6da9574151020d186279419f" ON "public"."country"("alpha_2_code");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_9f88595b715818e292be3472256" ON "public"."country"("alpha_3_code");

-- CreateIndex
CREATE INDEX "event_organization_title_idx" ON "public"."event_organization" USING GIN ("title" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "great_area_expertise_name_idx" ON "public"."great_area_expertise" USING GIN ("name" gin_trgm_ops);

-- CreateIndex
CREATE UNIQUE INDEX "UQ_d218ad3566afa9e396f184fd7d5" ON "public"."institution"("name");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_c50c675ba2bedbaff7192b0a30e" ON "public"."institution"("acronym");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_c9af99711dccbeb22b20b24cca8" ON "public"."institution"("cnpj");

-- CreateIndex
CREATE UNIQUE INDEX "openalex_researcher_researcher_id_key" ON "public"."openalex_researcher"("researcher_id");

-- CreateIndex
CREATE INDEX "periodical_magazine_name_idx" ON "public"."periodical_magazine" USING GIN ("name" gin_trgm_ops);

-- CreateIndex
CREATE UNIQUE INDEX "research_dictionary_term_type__key" ON "public"."research_dictionary"("term", "type_");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_fdf2bde0f46501e3e84ec154c32" ON "public"."researcher"("lattes_id");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_cd7166a27f090d19d4e985592db" ON "public"."researcher"("lattes_10_id");

-- CreateIndex
CREATE INDEX "researcher_abstract_en_idx" ON "public"."researcher" USING GIN ("abstract_en" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "researcher_abstract_idx" ON "public"."researcher" USING GIN ("abstract" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "researcher_name_idx" ON "public"."researcher" USING GIN ("name" gin_trgm_ops);

-- CreateIndex
CREATE INDEX "software_title_idx" ON "public"."software" USING GIN ("title" gin_trgm_ops);

-- CreateIndex
CREATE UNIQUE INDEX "UQ_b2c4aef5929860729007ac32f6f" ON "public"."state"("name");

-- CreateIndex
CREATE UNIQUE INDEX "UQ_a4925b2350673eb963998d27ec3" ON "public"."state"("abbreviation");

-- AddForeignKey
ALTER TABLE "admin"."graduate_program" ADD CONSTRAINT "graduate_program_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "admin"."institution"("institution_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."graduate_program_researcher" ADD CONSTRAINT "graduate_program_researcher_graduate_program_id_fkey" FOREIGN KEY ("graduate_program_id") REFERENCES "admin"."graduate_program"("graduate_program_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."graduate_program_researcher" ADD CONSTRAINT "graduate_program_researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "admin"."researcher"("researcher_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."graduate_program_student" ADD CONSTRAINT "graduate_program_student_graduate_program_id_fkey" FOREIGN KEY ("graduate_program_id") REFERENCES "admin"."graduate_program"("graduate_program_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."graduate_program_student" ADD CONSTRAINT "graduate_program_student_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "admin"."researcher"("researcher_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."permission" ADD CONSTRAINT "permission_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "admin"."roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."researcher_institution" ADD CONSTRAINT "researcher_institution_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "admin"."institution"("institution_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."researcher_institution" ADD CONSTRAINT "researcher_institution_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "admin"."researcher"("researcher_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."users" ADD CONSTRAINT "users_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "admin"."institution"("institution_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."users_roles" ADD CONSTRAINT "users_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "admin"."roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."users_roles" ADD CONSTRAINT "users_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "admin"."users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin"."weights" ADD CONSTRAINT "weights_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "admin"."institution"("institution_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."department_researcher" ADD CONSTRAINT "department_researcher_dep_id_fkey" FOREIGN KEY ("dep_id") REFERENCES "admin_ufmg"."department"("dep_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."department_researcher" ADD CONSTRAINT "department_researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "admin"."researcher"("researcher_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."department_technician" ADD CONSTRAINT "department_technician_dep_id_fkey" FOREIGN KEY ("dep_id") REFERENCES "admin_ufmg"."department"("dep_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."department_technician" ADD CONSTRAINT "department_technician_technician_id_fkey" FOREIGN KEY ("technician_id") REFERENCES "admin_ufmg"."technician"("technician_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."disciplines" ADD CONSTRAINT "disciplines_dep_id_fkey" FOREIGN KEY ("dep_id") REFERENCES "admin_ufmg"."department"("dep_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_ufmg"."researcher" ADD CONSTRAINT "researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "admin"."researcher"("researcher_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."abstract" ADD CONSTRAINT "abstract_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."article" ADD CONSTRAINT "article_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."article_abstract" ADD CONSTRAINT "article_abstract_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."openalex_article"("article_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."book" ADD CONSTRAINT "book_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."event" ADD CONSTRAINT "event_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."patent" ADD CONSTRAINT "patent_reference_id_fkey" FOREIGN KEY ("reference_id") REFERENCES "public"."patent"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."area_expertise" ADD CONSTRAINT "FK_great_area_expertise" FOREIGN KEY ("great_area_expertise_id") REFERENCES "public"."great_area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."area_specialty" ADD CONSTRAINT "area_specialty_sub_area_expertise_id_fkey" FOREIGN KEY ("sub_area_expertise_id") REFERENCES "public"."sub_area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."artistic_production" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production" ADD CONSTRAINT "FKCountryResearcher" FOREIGN KEY ("country_id") REFERENCES "public"."country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production_article" ADD CONSTRAINT "FKPeriodicalMagazineArticle" FOREIGN KEY ("periodical_magazine_id") REFERENCES "public"."periodical_magazine"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production_article" ADD CONSTRAINT "FKPublicationArticle" FOREIGN KEY ("bibliographic_production_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production_book" ADD CONSTRAINT "FKPublicationBook" FOREIGN KEY ("bibliographic_production_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production_book_chapter" ADD CONSTRAINT "FKPublicationBookChapter" FOREIGN KEY ("bibliographic_production_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."bibliographic_production_work_in_event" ADD CONSTRAINT "fk_bibliographic_production_event_work_production" FOREIGN KEY ("bibliographic_production_id") REFERENCES "public"."bibliographic_production"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."brand" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."city" ADD CONSTRAINT "FKCountryCity" FOREIGN KEY ("country_id") REFERENCES "public"."country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."city" ADD CONSTRAINT "FKStateCity" FOREIGN KEY ("state_id") REFERENCES "public"."state"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."didactic_material" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."education" ADD CONSTRAINT "fk_researcher_education" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."event_organization" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."foment" ADD CONSTRAINT "foment_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."graduate_program" ADD CONSTRAINT "graduate_program_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "public"."institution"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."graduate_program_researcher" ADD CONSTRAINT "graduate_program_researcher_graduate_program_id_fkey" FOREIGN KEY ("graduate_program_id") REFERENCES "public"."graduate_program"("graduate_program_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."graduate_program_researcher" ADD CONSTRAINT "graduate_program_researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."graduate_program_student" ADD CONSTRAINT "graduate_program_student_graduate_program_id_fkey" FOREIGN KEY ("graduate_program_id") REFERENCES "public"."graduate_program"("graduate_program_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."graduate_program_student" ADD CONSTRAINT "graduate_program_student_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."guidance" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."openalex_researcher" ADD CONSTRAINT "fk_researcher_op" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."participation_events" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."patent" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."relevant_production" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_lines_programs" ADD CONSTRAINT "research_lines_programs_graduate_program_id_fkey" FOREIGN KEY ("graduate_program_id") REFERENCES "public"."graduate_program"("graduate_program_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_project" ADD CONSTRAINT "research_project_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_project_components" ADD CONSTRAINT "research_project_components_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."research_project"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_project_foment" ADD CONSTRAINT "research_project_foment_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."research_project"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_project_production" ADD CONSTRAINT "research_project_production_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."research_project"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."research_report" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher" ADD CONSTRAINT "FKCityResearcher" FOREIGN KEY ("city_id") REFERENCES "public"."city"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher" ADD CONSTRAINT "FKCountryResearcher" FOREIGN KEY ("country_id") REFERENCES "public"."country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher" ADD CONSTRAINT "FKInstitutionResearcher" FOREIGN KEY ("institution_id") REFERENCES "public"."institution"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_address" ADD CONSTRAINT "FKAddressResearcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_area_expertise" ADD CONSTRAINT "FKResearcherAreaExpertise" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_area_expertise" ADD CONSTRAINT "FKSubAreaExpertise" FOREIGN KEY ("sub_area_expertise_id") REFERENCES "public"."sub_area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_area_expertise" ADD CONSTRAINT "FkAreaExpertise" FOREIGN KEY ("area_expertise_id") REFERENCES "public"."area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_area_expertise" ADD CONSTRAINT "FkAreaSpecialty" FOREIGN KEY ("area_specialty_id") REFERENCES "public"."area_specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_area_expertise" ADD CONSTRAINT "FkGreatAreaExpertise" FOREIGN KEY ("great_area_expertise_id") REFERENCES "public"."great_area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_ind_prod" ADD CONSTRAINT "FKRIndProd" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_production" ADD CONSTRAINT "researcher_production_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."researcher_professional_experience" ADD CONSTRAINT "researcher_professional_experience_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."software" ADD CONSTRAINT "fk_researcher_id" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."state" ADD CONSTRAINT "FKCountryState" FOREIGN KEY ("country_id") REFERENCES "public"."country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."sub_area_expertise" ADD CONSTRAINT "sub_area_expertise_area_expertise_id_fkey" FOREIGN KEY ("area_expertise_id") REFERENCES "public"."area_expertise"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."technical_work" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."technical_work_presentation" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."technical_work_program" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."technological_product" ADD CONSTRAINT "fk_researcher" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ufmg"."departament_researcher" ADD CONSTRAINT "departament_researcher_dep_id_fkey" FOREIGN KEY ("dep_id") REFERENCES "ufmg"."departament"("dep_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ufmg"."departament_researcher" ADD CONSTRAINT "departament_researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ufmg"."departament_technician" ADD CONSTRAINT "departament_technician_dep_id_fkey" FOREIGN KEY ("dep_id") REFERENCES "ufmg"."departament"("dep_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ufmg"."departament_technician" ADD CONSTRAINT "departament_technician_technician_id_fkey" FOREIGN KEY ("technician_id") REFERENCES "ufmg"."technician"("technician_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ufmg"."researcher" ADD CONSTRAINT "researcher_researcher_id_fkey" FOREIGN KEY ("researcher_id") REFERENCES "public"."researcher"("id") ON DELETE CASCADE ON UPDATE CASCADE;