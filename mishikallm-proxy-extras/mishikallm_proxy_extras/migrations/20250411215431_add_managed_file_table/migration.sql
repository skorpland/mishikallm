-- CreateTable
CREATE TABLE "MishikaLLM_ManagedFileTable" (
    "id" TEXT NOT NULL,
    "unified_file_id" TEXT NOT NULL,
    "file_object" JSONB NOT NULL,
    "model_mappings" JSONB NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MishikaLLM_ManagedFileTable_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "MishikaLLM_ManagedFileTable_unified_file_id_key" ON "MishikaLLM_ManagedFileTable"("unified_file_id");

-- CreateIndex
CREATE INDEX "MishikaLLM_ManagedFileTable_unified_file_id_idx" ON "MishikaLLM_ManagedFileTable"("unified_file_id");

