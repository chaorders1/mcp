# MCP Curl PRD

## Overview

A Model Context Protocol (MCP) server that enables executing curl commands through natural language requests. The server implements a plugin-like architecture for handling different API services through curl.

## Core Features

### 1. Modular Handler System

- Base Handler Interface (`CurlHandler`)
  - Name property
  - Description property
  - Input schema definition
  - Curl command builder
  - Common execution logic

### 2. Built-in Handlers

#### Railway Handlers
- Health Check (`railway-health`)
  - Check service status
  - No required parameters
  - GET request with JSON headers
- File Processing (`railway-process-file`)
  - Process files through API
  - Required: file_path
  - Optional: format, options
  - POST request with JSON data

#### Ollama Handler
- Text Generation (`ollama-generate`)
  - Generate text using models
  - Required: prompt
  - Optional: model, temperature, stream
  - POST request with complex JSON data

#### Firecrawl Handler
- Web Scraping (`firecrawl-scrape`)
  - Scrape webpage content
  - Required: url
  - Optional: formats (markdown/html/links)
  - POST request with Bearer authentication

### 3. Extensibility

- Plugin Architecture
  - Easy handler addition
  - Standardized interface
  - Independent curl command building
  - Common execution logic in base class

### 4. Security

- Environment-based Configuration
  - API keys management
  - Service URLs configuration
  - Secure credential handling
  - Curl command sanitization

## Technical Requirements

### Server
- Python 3.10+
- curl command-line tool
- Environment configuration
- Error handling and logging

### Client
- MCP protocol support
- Async communication
- JSON schema validation

## Future Enhancements

1. Handler Discovery
   - Dynamic handler loading
   - Hot-reload support
   - Version management

2. Curl Command Enhancement
   - Advanced curl options support
   - Custom header management
   - Certificate handling
   - Proxy support

3. Monitoring
   - Request tracking
   - Performance metrics
   - Usage analytics
   - Curl command logging
