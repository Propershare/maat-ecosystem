-- AlterTable
ALTER TABLE "StageDefinition" ADD COLUMN     "canon_reference" TEXT NOT NULL DEFAULT 'UKMT_EDUCATION_PIPELINE_TABLE_V1',
ADD COLUMN     "stepwise_build_actions" TEXT NOT NULL DEFAULT '';
