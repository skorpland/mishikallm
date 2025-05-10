-- AlterTable
ALTER TABLE "MishikaLLM_TeamTable" ADD COLUMN     "team_member_permissions" TEXT[] DEFAULT ARRAY[]::TEXT[];

