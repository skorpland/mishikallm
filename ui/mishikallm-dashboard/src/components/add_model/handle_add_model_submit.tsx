import { message } from "antd";
import { provider_map, Providers } from "../provider_info_helpers";
import { modelCreateCall, Model, testConnectionRequest } from "../networking";
import React, { useState } from 'react';
import ConnectionErrorDisplay from './model_connection_test';

export const prepareModelAddRequest = async (
    formValues: Record<string, any>,
    accessToken: string,
    form: any,
  ) => {
    try {
      console.log("handling submit for formValues:", formValues);


      // Get model mappings and safely remove from formValues
      const modelMappings = formValues["model_mappings"] || [];
      if ("model_mappings" in formValues) {
        delete formValues["model_mappings"];
      }
      
      
      // Handle wildcard case
      if (formValues["model"] && formValues["model"].includes("all-wildcard")) {
        const customProvider: Providers = formValues["custom_llm_provider"];
        const mishikallm_custom_provider = provider_map[customProvider as keyof typeof Providers];
        const wildcardModel = mishikallm_custom_provider + "/*";
        formValues["model_name"] = wildcardModel;
        modelMappings.push({
          public_name: wildcardModel,
          mishikallm_model: wildcardModel,
        });
        formValues["model"] = wildcardModel; 
      }

      // Create a deployment for each mapping
      const deployments = [];
      for (const mapping of modelMappings) {
        const mishikallmParamsObj: Record<string, any> = {};
        const modelInfoObj: Record<string, any> = {};
        
        // Set the model name and mishikallm model from the mapping
        const modelName = mapping.public_name;
        mishikallmParamsObj["model"] = mapping.mishikallm_model;

        // Handle pricing conversion before processing other fields
        if (formValues.input_cost_per_token) {
          formValues.input_cost_per_token = Number(formValues.input_cost_per_token) / 1000000;
        }
        if (formValues.output_cost_per_token) {
          formValues.output_cost_per_token = Number(formValues.output_cost_per_token) / 1000000;
        }
        // Keep input_cost_per_second as is, no conversion needed
        
        // Iterate through the key-value pairs in formValues
        mishikallmParamsObj["model"] = mapping.mishikallm_model;
        console.log("formValues add deployment:", formValues);
        for (const [key, value] of Object.entries(formValues)) {
          if (value === "") {
            continue;
          }
          // Skip the custom_pricing and pricing_model fields as they're only used for UI control
          if (key === 'custom_pricing' || key === 'pricing_model' || key === 'cache_control') {
            continue;
          }
          if (key == "model_name") {
            mishikallmParamsObj["model"] = value;
          } else if (key == "custom_llm_provider") {
            console.log("custom_llm_provider:", value);
            const mappingResult = provider_map[value]; // Get the corresponding value from the mapping
            mishikallmParamsObj["custom_llm_provider"] = mappingResult;
            console.log("custom_llm_provider mappingResult:", mappingResult);
          } else if (key == "model") {
            continue;
          }
          // Check if key is "base_model"
          else if (key === "base_model") {
            // Add key-value pair to model_info dictionary
            modelInfoObj[key] = value;
          }
          else if (key === "team_id") {
            modelInfoObj["team_id"] = value;
          }
          else if (key == "mode") {
            console.log("placing mode in modelInfo")
            modelInfoObj["mode"] = value;

            // remove "mode" from mishikallmParams
            delete mishikallmParamsObj["mode"];
          }
          else if (key === "custom_model_name") {
            mishikallmParamsObj["model"] = value;
          } else if (key == "mishikallm_extra_params") {
            console.log("mishikallm_extra_params:", value);
            let mishikallmExtraParams = {};
            if (value && value != undefined) {
              try {
                mishikallmExtraParams = JSON.parse(value);
              } catch (error) {
                message.error(
                  "Failed to parse MishikaLLM Extra Params: " + error,
                  10
                );
                throw new Error("Failed to parse mishikallm_extra_params: " + error);
              }
              for (const [key, value] of Object.entries(mishikallmExtraParams)) {
                mishikallmParamsObj[key] = value;
              }
            }
          } else if (key == "model_info_params") {
            console.log("model_info_params:", value);
            let modelInfoParams = {};
            if (value && value != undefined) {
              try {
                modelInfoParams = JSON.parse(value);
              } catch (error) {
                message.error(
                  "Failed to parse MishikaLLM Extra Params: " + error,
                  10
                );
                throw new Error("Failed to parse mishikallm_extra_params: " + error);
              }
              for (const [key, value] of Object.entries(modelInfoParams)) {
                modelInfoObj[key] = value;
              }
            }
          }
  
          // Handle the pricing fields
          else if (key === "input_cost_per_token" || 
                  key === "output_cost_per_token" || 
                  key === "input_cost_per_second") {
            if (value) {
              mishikallmParamsObj[key] = Number(value);
            }
            continue;
          }
  
          // Check if key is any of the specified API related keys
          else {
            // Add key-value pair to mishikallm_params dictionary
            mishikallmParamsObj[key] = value;
          }
        }

        deployments.push({ mishikallmParamsObj, modelInfoObj, modelName });
      }

      return deployments;
    } catch (error) {
      message.error("Failed to create model: " + error, 10);
    }
  };

export const handleAddModelSubmit = async (
    values: any,
    accessToken: string,
    form: any,
    callback?: () => void,
  ) => {
    try {
      const deployments = await prepareModelAddRequest(values, accessToken, form);
      
      if (!deployments || deployments.length === 0) {
        return; // Exit if preparation failed or no deployments
      }
      
      // Create each deployment
      for (const deployment of deployments) {
        const { mishikallmParamsObj, modelInfoObj, modelName } = deployment;
        
        const new_model: Model = {
          model_name: modelName,
          mishikallm_params: mishikallmParamsObj,
          model_info: modelInfoObj,
        };
        
        const response: any = await modelCreateCall(accessToken, new_model);
        console.log(`response for model create call: ${response["data"]}`);
      }
      
      callback && callback();
      form.resetFields();
    } catch (error) {
      message.error("Failed to add model: " + error, 10);
    }
  };

     
