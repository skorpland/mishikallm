-- AlterTable
ALTER TABLE "MishikaLLM_DailyUserSpend" ADD COLUMN     "failed_requests" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "successful_requests" INTEGER NOT NULL DEFAULT 0;

