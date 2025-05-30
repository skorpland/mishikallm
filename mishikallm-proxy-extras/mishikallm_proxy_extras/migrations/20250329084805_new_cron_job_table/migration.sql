-- CreateEnum
CREATE TYPE "JobStatus" AS ENUM ('ACTIVE', 'INACTIVE');

-- CreateTable
CREATE TABLE "MishikaLLM_CronJob" (
    "cronjob_id" TEXT NOT NULL,
    "pod_id" TEXT NOT NULL,
    "status" "JobStatus" NOT NULL DEFAULT 'INACTIVE',
    "last_updated" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ttl" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MishikaLLM_CronJob_pkey" PRIMARY KEY ("cronjob_id")
);

