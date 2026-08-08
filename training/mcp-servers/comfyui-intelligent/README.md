# intelligent-comfyui-mcp

**Maat-Aligned Tool Documentation**

## Overview

intelligent-comfyui-mcp MCP Server

**Version**: 1.25.0  
**Total Tools**: 30

## Maat Principles Alignment

### Truth (Maat)
ComfyUI workflow generation and image processing

### Balance (Maat)
Balance creative freedom with workflow structure

### Order (Maat)
Systematic workflow generation

### Justice (Maat)
Proper workflow attribution

### Self-Reflection (Maat)
Learn from workflow patterns

## Available Tools

### List Models

**Operation ID**: `tool_list_models_post`  
**Path**: `POST /list_models`

List available models. Filter by type (diffusion, text_encoder, vae) or capability (image_to_video, text_to_video, etc.)

**Request Body**: See OpenAPI spec for schema details

### List Workflows

**Operation ID**: `tool_list_workflows_post`  
**Path**: `POST /list_workflows`

List all available workflows and their capabilities

### Get Best Model

**Operation ID**: `tool_get_best_model_post`  
**Path**: `POST /get_best_model`

Get the best model for a capability, optionally constrained by VRAM

**Request Body**: See OpenAPI spec for schema details

### Get Execution Statistics

**Operation ID**: `tool_get_execution_statistics_post`  
**Path**: `POST /get_execution_statistics`

Get statistics about workflow executions

**Request Body**: See OpenAPI spec for schema details

### Search Workflows

**Operation ID**: `tool_search_workflows_post`  
**Path**: `POST /search_workflows`

Search workflows by specifications (capability, input type, output type, model family, etc.)

**Request Body**: See OpenAPI spec for schema details

### Get Workflow Specs

**Operation ID**: `tool_get_workflow_specs_post`  
**Path**: `POST /get_workflow_specs`

Get detailed specifications for a workflow

**Request Body**: See OpenAPI spec for schema details

### Get Model Settings

**Operation ID**: `tool_get_model_settings_post`  
**Path**: `POST /get_model_settings`

Get best settings for a model (resolution, steps, cfg, sampler, etc.) for training/optimization

**Request Body**: See OpenAPI spec for schema details

### Get Training Recommendations

**Operation ID**: `tool_get_training_recommendations_post`  
**Path**: `POST /get_training_recommendations`

Get training/optimization recommendations for a model

**Request Body**: See OpenAPI spec for schema details

### Get Version

**Operation ID**: `tool_get_version_post`  
**Path**: `POST /get_version`

Get the MCP server version and build information

### Get Execution Status

**Operation ID**: `tool_get_execution_status_post`  
**Path**: `POST /get_execution_status`

Get the status of a workflow execution by execution ID

**Request Body**: See OpenAPI spec for schema details

### List Executions

**Operation ID**: `tool_list_executions_post`  
**Path**: `POST /list_executions`

List recent workflow executions with optional filters

**Request Body**: See OpenAPI spec for schema details

### Validate Workflow

**Operation ID**: `tool_validate_workflow_post`  
**Path**: `POST /validate_workflow`

Validate workflow accuracy and check if download is needed. Returns accuracy score, errors, and recommendations.

**Request Body**: See OpenAPI spec for schema details

### Check Workflow Accuracy

**Operation ID**: `tool_check_workflow_accuracy_post`  
**Path**: `POST /check_workflow_accuracy`

Check workflow accuracy and get detailed report. Will indicate if workflow needs to be downloaded.

**Request Body**: See OpenAPI spec for schema details

### Download Model

**Operation ID**: `tool_download_model_post`  
**Path**: `POST /download_model`

Download a model from Hugging Face Hub. Returns download status and file path.

**Request Body**: See OpenAPI spec for schema details

### Download Workflow

**Operation ID**: `tool_download_workflow_post`  
**Path**: `POST /download_workflow`

Download a workflow JSON from Hugging Face Hub or URL.

**Request Body**: See OpenAPI spec for schema details

### Search Models

**Operation ID**: `tool_search_models_post`  
**Path**: `POST /search_models`

Search for models on Hugging Face Hub by query.

**Request Body**: See OpenAPI spec for schema details

### Install Custom Node

**Operation ID**: `tool_install_custom_node_post`  
**Path**: `POST /install_custom_node`

Install a custom node using ComfyUI-Manager. Required for workflows that depend on custom nodes.

**Request Body**: See OpenAPI spec for schema details

### Check Missing Nodes

**Operation ID**: `tool_check_missing_nodes_post`  
**Path**: `POST /check_missing_nodes`

Check if a workflow has missing custom nodes that need to be installed.

**Request Body**: See OpenAPI spec for schema details

### Install Missing Nodes

**Operation ID**: `tool_install_missing_nodes_post`  
**Path**: `POST /install_missing_nodes`

Automatically install missing custom nodes required by a workflow.

**Request Body**: See OpenAPI spec for schema details

### Load Workflow To Canvas

**Operation ID**: `tool_load_workflow_to_canvas_post`  
**Path**: `POST /load_workflow_to_canvas`

Load a workflow JSON file into ComfyUI canvas. Opens the workflow in the web interface for viewing/editing.

**Request Body**: See OpenAPI spec for schema details

### Execute Wan2.2 I2V

**Operation ID**: `tool_execute_wan2_2_i2v_post`  
**Path**: `POST /execute_wan2.2_i2v`

CALL THIS TOOL to transform or modify an image based on a text prompt. Returns a result_url with the generated image., CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image., CALL THIS TOOL to generate a video from an image and text prompt. Returns a result_url with the generated video., CALL THIS TOOL to generate a video from a text prompt. Returns a result_url with the generated video.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Basic

**Operation ID**: `tool_execute_txt2img_basic_post`  
**Path**: `POST /execute_txt2img_basic`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Realvisxl V5 Full

**Operation ID**: `tool_execute_txt2img_realvisxl_v5_full_post`  
**Path**: `POST /execute_txt2img_realvisxl_v5_full`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Example Download Test

**Operation ID**: `tool_execute_example_download_test_post`  
**Path**: `POST /execute_example_download_test`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Img2Img Basic

**Operation ID**: `tool_execute_img2img_basic_post`  
**Path**: `POST /execute_img2img_basic`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image., CALL THIS TOOL to transform or modify an image based on a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Sd15

**Operation ID**: `tool_execute_txt2img_sd15_post`  
**Path**: `POST /execute_txt2img_sd15`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Realvisxl V5 With Lora

**Operation ID**: `tool_execute_txt2img_realvisxl_v5_with_lora_post`  
**Path**: `POST /execute_txt2img_realvisxl_v5_with_lora`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Realvisxl V5

**Operation ID**: `tool_execute_txt2img_realvisxl_v5_post`  
**Path**: `POST /execute_txt2img_realvisxl_v5`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Chroma1-Hd-Df11

**Operation ID**: `tool_execute_Chroma1_HD_DF11_post`  
**Path**: `POST /execute_Chroma1-HD-DF11`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

### Execute Txt2Img Chroma Hd

**Operation ID**: `tool_execute_txt2img_chroma_hd_post`  
**Path**: `POST /execute_txt2img_chroma_hd`

CALL THIS TOOL to generate an image from a text prompt. Returns a result_url with the generated image.. REQUIRED parameter: 'text' (the prompt). Returns JSON with 'result_url' field containing the image/video URL.

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- Generate images
- Edit images
- Create workflows
- Execute workflows

## Common Patterns

- Prompt → Generate workflow → Execute → Return image

## Tool Selection Decision Tree

1. **Identify the task domain**
   - System operations → `tehuti-core`
   - Workflow automation → `n8n-mcp`
   - File operations → `filesystem-mcp`
   - Database queries → `postgres-mcp`
   - Image generation → `comfyui-intelligent`
   - Audio generation → `tehuti-audio`
   - RAG/Knowledge → `maatlangchain-pipeline`

2. **Check tool availability**
   - Verify tool is accessible (port check)
   - Check OpenAPI spec for available operations

3. **Select appropriate tool**
   - Match user intent to tool capability
   - Consider tool chaining for complex tasks

4. **Execute with Maat principles**
   - Truth: Accurate parameters
   - Balance: Appropriate tool selection
   - Order: Systematic execution
   - Justice: Proper attribution
   - Self-Reflection: Learn from results

## Error Handling

Common errors and solutions:

- **Connection Error**: Check if MCP server is running on expected port
- **Parameter Error**: Verify parameter types match OpenAPI spec
- **Timeout Error**: Increase timeout or optimize operation
- **Permission Error**: Check file/database permissions

## Best Practices

1. Always validate parameters before tool execution
2. Use appropriate timeouts for long-running operations
3. Log tool usage to gitMaat for learning
4. Chain tools systematically for complex tasks
5. Handle errors gracefully with informative messages

## Related Tools

See `training/schemas/tool-relationships.json` for tool dependency information.

---
**Maat Alignment**: This documentation follows Maat principles of Truth, Balance, Order, Justice, and Self-Reflection.
