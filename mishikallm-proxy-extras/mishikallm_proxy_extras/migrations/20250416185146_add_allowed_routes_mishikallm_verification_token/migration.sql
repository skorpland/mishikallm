-- AlterTable
ALTER TABLE "MishikaLLM_VerificationToken" ADD COLUMN     "allowed_routes" TEXT[] DEFAULT ARRAY[]::TEXT[];

