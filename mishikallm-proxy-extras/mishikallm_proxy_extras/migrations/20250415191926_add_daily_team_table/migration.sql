-- CreateTable
CREATE TABLE "MishikaLLM_DailyTeamSpend" (
    "id" TEXT NOT NULL,
    "team_id" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "api_key" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "model_group" TEXT,
    "custom_llm_provider" TEXT,
    "prompt_tokens" INTEGER NOT NULL DEFAULT 0,
    "completion_tokens" INTEGER NOT NULL DEFAULT 0,
    "spend" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "api_requests" INTEGER NOT NULL DEFAULT 0,
    "successful_requests" INTEGER NOT NULL DEFAULT 0,
    "failed_requests" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MishikaLLM_DailyTeamSpend_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "MishikaLLM_DailyTeamSpend_date_idx" ON "MishikaLLM_DailyTeamSpend"("date");

-- CreateIndex
CREATE INDEX "MishikaLLM_DailyTeamSpend_team_id_idx" ON "MishikaLLM_DailyTeamSpend"("team_id");

-- CreateIndex
CREATE INDEX "MishikaLLM_DailyTeamSpend_api_key_idx" ON "MishikaLLM_DailyTeamSpend"("api_key");

-- CreateIndex
CREATE INDEX "MishikaLLM_DailyTeamSpend_model_idx" ON "MishikaLLM_DailyTeamSpend"("model");

-- CreateIndex
CREATE UNIQUE INDEX "MishikaLLM_DailyTeamSpend_team_id_date_api_key_model_custom_ll_key" ON "MishikaLLM_DailyTeamSpend"("team_id", "date", "api_key", "model", "custom_llm_provider");

