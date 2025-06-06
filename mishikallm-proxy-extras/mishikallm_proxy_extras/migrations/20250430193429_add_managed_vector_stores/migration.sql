-- CreateTable
CREATE TABLE "MishikaLLM_ManagedVectorStoresTable" (
    "vector_store_id" TEXT NOT NULL,
    "custom_llm_provider" TEXT NOT NULL,
    "vector_store_name" TEXT,
    "vector_store_description" TEXT,
    "vector_store_metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "mishikallm_credential_name" TEXT,

    CONSTRAINT "MishikaLLM_ManagedVectorStoresTable_pkey" PRIMARY KEY ("vector_store_id")
);

