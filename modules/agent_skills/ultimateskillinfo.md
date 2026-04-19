# JARVIS Ultimate Skill Info Catalog

This document provides a concise reference for all core tools and expert playbooks available in Jarvis Agentic Mode.

## 🛠️ Core Agentic Tools
These are Python-based capabilities that give Jarvis 'hands' to interact with your system.
- **control_app**: Open or quit macOS applications. Input: {'action': 'open'|'quit', 'app_name': str}. Example: {'action': 'open', 'app_name': 'Safari'}
- **get_weather**: Get current weather or forecast. Input: {'location': str}
- **read_source_file**: Read the content of a file in the JARVIS codebase. Input: {'path': 'relative/path/to/file.py'}
- **save_info**: Save a key piece of information to your internal memory vault for later use in this task. Input: {'key': str, 'value': str}. Example: {'key': 'news_summary', 'value': 'Apple released a new Mac...'}
- **search_openclaw_skills**: Search the official OpenClaw registry of 5000+ skills when you need a capability you do not currently have. Input: {'query': str}
- **send_email**: Send an email. Input: {'recipient': str, 'subject': str, 'body': str}. Requires confirmation.
- **web_search**: Search the internet for information. Input: {'query': str}

## 🧠 Expert Playbooks (@id)
These are cognitive guidelines that give Jarvis 'brains' for specific expert roles. Mention the `@id` in your prompt to activate them.

### Table of Contents
- [00 Andruia Consultant](#00-andruia-consultant)
- [007](#007)
- [10 Andruia Skill Smith](#10-andruia-skill-smith)
- [20 Andruia Niche Intelligence](#20-andruia-niche-intelligence)
- [3D Web Experience](#3d-web-experience)
- [Ab Test Setup](#ab-test-setup)
- [Acceptance Orchestrator](#acceptance-orchestrator)
- [Accessibility Compliance Accessibility Audit](#accessibility-compliance-accessibility-audit)
- [Active Directory Attacks](#active-directory-attacks)
- [Activecampaign Automation](#activecampaign-automation)
- [Ad Creative](#ad-creative)
- [Address Github Comments](#address-github-comments)
- [Adhx](#adhx)
- [Advanced Evaluation](#advanced-evaluation)
- [Advogado Criminal](#advogado-criminal)
- [Advogado Especialista](#advogado-especialista)
- [Aegisops Ai](#aegisops-ai)
- [Agent Evaluation](#agent-evaluation)
- [Agent Framework Azure Ai Py](#agent-framework-azure-ai-py)
- [Agent Manager Skill](#agent-manager-skill)
- [Agent Memory Mcp](#agent-memory-mcp)
- [Agent Memory Systems](#agent-memory-systems)
- [Agent Orchestration Improve Agent](#agent-orchestration-improve-agent)
- [Agent Orchestration Multi Agent Optimize](#agent-orchestration-multi-agent-optimize)
- [Agent Orchestrator](#agent-orchestrator)
- [Agent Tool Builder](#agent-tool-builder)
- [Agentflow](#agentflow)
- [Agentfolio](#agentfolio)
- [Agentic Actions Auditor](#agentic-actions-auditor)
- [Agentmail](#agentmail)
- [Agentphone](#agentphone)
- [Agents Md](#agents-md)
- [Ai Agent Development](#ai-agent-development)
- [Ai Agents Architect](#ai-agents-architect)
- [Ai Analyzer](#ai-analyzer)
- [Ai Engineering Toolkit](#ai-engineering-toolkit)
- [Ai Md](#ai-md)
- [Ai Ml](#ai-ml)
- [Ai Native Cli](#ai-native-cli)
- [Ai Product](#ai-product)
- [Ai Seo](#ai-seo)
- [Ai Studio Image](#ai-studio-image)
- [Ai Wrapper Product](#ai-wrapper-product)
- [Airflow Dag Patterns](#airflow-dag-patterns)
- [Airtable Automation](#airtable-automation)
- [Akf Trust Metadata](#akf-trust-metadata)
- [Algolia Search](#algolia-search)
- [Alpha Vantage](#alpha-vantage)
- [Amazon Alexa](#amazon-alexa)
- [Amplitude Automation](#amplitude-automation)
- [Analytics Product](#analytics-product)
- [Analytics Tracking](#analytics-tracking)
- [Analyze Project](#analyze-project)
- [Andrej Karpathy](#andrej-karpathy)
- [Android Jetpack Compose Expert](#android-jetpack-compose-expert)
- [Android_Ui_Verification](#android_ui_verification)
- [Angular](#angular)
- [Angular Best Practices](#angular-best-practices)
- [Angular Migration](#angular-migration)
- [Angular State Management](#angular-state-management)
- [Angular Ui Patterns](#angular-ui-patterns)
- [Animejs Animation](#animejs-animation)
- [Anti Reversing Techniques](#anti-reversing-techniques)
- [Antigravity Design Expert](#antigravity-design-expert)
- [Antigravity Skill Orchestrator](#antigravity-skill-orchestrator)
- [Antigravity Workflows](#antigravity-workflows)
- [Api Design Principles](#api-design-principles)
- [Api Documentation](#api-documentation)
- [Api Documentation Generator](#api-documentation-generator)
- [Api Endpoint Builder](#api-endpoint-builder)
- [Api Fuzzing Bug Bounty](#api-fuzzing-bug-bounty)
- [Api Patterns](#api-patterns)
- [Api Security Best Practices](#api-security-best-practices)
- [Api Security Testing](#api-security-testing)
- [Api Testing Observability Api Mock](#api-testing-observability-api-mock)
- [Apify Actor Development](#apify-actor-development)
- [Apify Actorization](#apify-actorization)
- [Apify Audience Analysis](#apify-audience-analysis)
- [Apify Brand Reputation Monitoring](#apify-brand-reputation-monitoring)
- [Apify Competitor Intelligence](#apify-competitor-intelligence)
- [Apify Content Analytics](#apify-content-analytics)
- [Apify Ecommerce](#apify-ecommerce)
- [Apify Influencer Discovery](#apify-influencer-discovery)
- [Apify Lead Generation](#apify-lead-generation)
- [Apify Market Research](#apify-market-research)
- [Apify Trend Analysis](#apify-trend-analysis)
- [Apify Ultimate Scraper](#apify-ultimate-scraper)
- [App Builder](#app-builder)
- [App Store Changelog](#app-store-changelog)
- [App Store Optimization](#app-store-optimization)
- [Appdeploy](#appdeploy)
- [Architecture](#architecture)
- [Architecture Decision Records](#architecture-decision-records)
- [Architecture Patterns](#architecture-patterns)
- [Arm Cortex Expert](#arm-cortex-expert)
- [Asana Automation](#asana-automation)
- [Ask Questions If Underspecified](#ask-questions-if-underspecified)
- [Astro](#astro)
- [Astropy](#astropy)
- [Async Python Patterns](#async-python-patterns)
- [Attack Tree Construction](#attack-tree-construction)
- [Audio Transcriber](#audio-transcriber)
- [Audit Context Building](#audit-context-building)
- [Audit Skills](#audit-skills)
- [Auri Core](#auri-core)
- [Auth Implementation Patterns](#auth-implementation-patterns)
- [Autonomous Agent Patterns](#autonomous-agent-patterns)
- [Autonomous Agents](#autonomous-agents)
- [Avalonia Layout Zafiro](#avalonia-layout-zafiro)
- [Avalonia Viewmodels Zafiro](#avalonia-viewmodels-zafiro)
- [Avalonia Zafiro Development](#avalonia-zafiro-development)
- [Avoid Ai Writing](#avoid-ai-writing)
- [Aws Cost Cleanup](#aws-cost-cleanup)
- [Aws Cost Optimizer](#aws-cost-optimizer)
- [Aws Penetration Testing](#aws-penetration-testing)
- [Aws Serverless](#aws-serverless)
- [Aws Skills](#aws-skills)
- [Awt E2E Testing](#awt-e2e-testing)
- [Azd Deployment](#azd-deployment)
- [Azure Ai Agents Persistent Dotnet](#azure-ai-agents-persistent-dotnet)
- [Azure Ai Agents Persistent Java](#azure-ai-agents-persistent-java)
- [Azure Ai Anomalydetector Java](#azure-ai-anomalydetector-java)
- [Azure Ai Contentsafety Java](#azure-ai-contentsafety-java)
- [Azure Ai Contentsafety Py](#azure-ai-contentsafety-py)
- [Azure Ai Contentsafety Ts](#azure-ai-contentsafety-ts)
- [Azure Ai Contentunderstanding Py](#azure-ai-contentunderstanding-py)
- [Azure Ai Document Intelligence Dotnet](#azure-ai-document-intelligence-dotnet)
- [Azure Ai Document Intelligence Ts](#azure-ai-document-intelligence-ts)
- [Azure Ai Formrecognizer Java](#azure-ai-formrecognizer-java)
- [Azure Ai Ml Py](#azure-ai-ml-py)
- [Azure Ai Openai Dotnet](#azure-ai-openai-dotnet)
- [Azure Ai Projects Dotnet](#azure-ai-projects-dotnet)
- [Azure Ai Projects Java](#azure-ai-projects-java)
- [Azure Ai Projects Py](#azure-ai-projects-py)
- [Azure Ai Projects Ts](#azure-ai-projects-ts)
- [Azure Ai Textanalytics Py](#azure-ai-textanalytics-py)
- [Azure Ai Transcription Py](#azure-ai-transcription-py)
- [Azure Ai Translation Document Py](#azure-ai-translation-document-py)
- [Azure Ai Translation Text Py](#azure-ai-translation-text-py)
- [Azure Ai Translation Ts](#azure-ai-translation-ts)
- [Azure Ai Vision Imageanalysis Java](#azure-ai-vision-imageanalysis-java)
- [Azure Ai Vision Imageanalysis Py](#azure-ai-vision-imageanalysis-py)
- [Azure Ai Voicelive Dotnet](#azure-ai-voicelive-dotnet)
- [Azure Ai Voicelive Java](#azure-ai-voicelive-java)
- [Azure Ai Voicelive Py](#azure-ai-voicelive-py)
- [Azure Ai Voicelive Ts](#azure-ai-voicelive-ts)
- [Azure Appconfiguration Java](#azure-appconfiguration-java)
- [Azure Appconfiguration Py](#azure-appconfiguration-py)
- [Azure Appconfiguration Ts](#azure-appconfiguration-ts)
- [Azure Communication Callautomation Java](#azure-communication-callautomation-java)
- [Azure Communication Callingserver Java](#azure-communication-callingserver-java)
- [Azure Communication Chat Java](#azure-communication-chat-java)
- [Azure Communication Common Java](#azure-communication-common-java)
- [Azure Communication Sms Java](#azure-communication-sms-java)
- [Azure Compute Batch Java](#azure-compute-batch-java)
- [Azure Containerregistry Py](#azure-containerregistry-py)
- [Azure Cosmos Db Py](#azure-cosmos-db-py)
- [Azure Cosmos Java](#azure-cosmos-java)
- [Azure Cosmos Py](#azure-cosmos-py)
- [Azure Cosmos Rust](#azure-cosmos-rust)
- [Azure Cosmos Ts](#azure-cosmos-ts)
- [Azure Data Tables Java](#azure-data-tables-java)
- [Azure Data Tables Py](#azure-data-tables-py)
- [Azure Eventgrid Dotnet](#azure-eventgrid-dotnet)
- [Azure Eventgrid Java](#azure-eventgrid-java)
- [Azure Eventgrid Py](#azure-eventgrid-py)
- [Azure Eventhub Dotnet](#azure-eventhub-dotnet)
- [Azure Eventhub Java](#azure-eventhub-java)
- [Azure Eventhub Py](#azure-eventhub-py)
- [Azure Eventhub Rust](#azure-eventhub-rust)
- [Azure Eventhub Ts](#azure-eventhub-ts)
- [Azure Functions](#azure-functions)
- [Azure Identity Dotnet](#azure-identity-dotnet)
- [Azure Identity Java](#azure-identity-java)
- [Azure Identity Py](#azure-identity-py)
- [Azure Identity Rust](#azure-identity-rust)
- [Azure Identity Ts](#azure-identity-ts)
- [Azure Keyvault Certificates Rust](#azure-keyvault-certificates-rust)
- [Azure Keyvault Keys Rust](#azure-keyvault-keys-rust)
- [Azure Keyvault Keys Ts](#azure-keyvault-keys-ts)
- [Azure Keyvault Py](#azure-keyvault-py)
- [Azure Keyvault Secrets Rust](#azure-keyvault-secrets-rust)
- [Azure Keyvault Secrets Ts](#azure-keyvault-secrets-ts)
- [Azure Maps Search Dotnet](#azure-maps-search-dotnet)
- [Azure Messaging Webpubsub Java](#azure-messaging-webpubsub-java)
- [Azure Messaging Webpubsubservice Py](#azure-messaging-webpubsubservice-py)
- [Azure Mgmt Apicenter Dotnet](#azure-mgmt-apicenter-dotnet)
- [Azure Mgmt Apicenter Py](#azure-mgmt-apicenter-py)
- [Azure Mgmt Apimanagement Dotnet](#azure-mgmt-apimanagement-dotnet)
- [Azure Mgmt Apimanagement Py](#azure-mgmt-apimanagement-py)
- [Azure Mgmt Applicationinsights Dotnet](#azure-mgmt-applicationinsights-dotnet)
- [Azure Mgmt Arizeaiobservabilityeval Dotnet](#azure-mgmt-arizeaiobservabilityeval-dotnet)
- [Azure Mgmt Botservice Dotnet](#azure-mgmt-botservice-dotnet)
- [Azure Mgmt Botservice Py](#azure-mgmt-botservice-py)
- [Azure Mgmt Fabric Dotnet](#azure-mgmt-fabric-dotnet)
- [Azure Mgmt Fabric Py](#azure-mgmt-fabric-py)
- [Azure Mgmt Mongodbatlas Dotnet](#azure-mgmt-mongodbatlas-dotnet)
- [Azure Mgmt Weightsandbiases Dotnet](#azure-mgmt-weightsandbiases-dotnet)
- [Azure Microsoft Playwright Testing Ts](#azure-microsoft-playwright-testing-ts)
- [Azure Monitor Ingestion Java](#azure-monitor-ingestion-java)
- [Azure Monitor Ingestion Py](#azure-monitor-ingestion-py)
- [Azure Monitor Opentelemetry Exporter Java](#azure-monitor-opentelemetry-exporter-java)
- [Azure Monitor Opentelemetry Exporter Py](#azure-monitor-opentelemetry-exporter-py)
- [Azure Monitor Opentelemetry Py](#azure-monitor-opentelemetry-py)
- [Azure Monitor Opentelemetry Ts](#azure-monitor-opentelemetry-ts)
- [Azure Monitor Query Java](#azure-monitor-query-java)
- [Azure Monitor Query Py](#azure-monitor-query-py)
- [Azure Postgres Ts](#azure-postgres-ts)
- [Azure Resource Manager Cosmosdb Dotnet](#azure-resource-manager-cosmosdb-dotnet)
- [Azure Resource Manager Durabletask Dotnet](#azure-resource-manager-durabletask-dotnet)
- [Azure Resource Manager Mysql Dotnet](#azure-resource-manager-mysql-dotnet)
- [Azure Resource Manager Playwright Dotnet](#azure-resource-manager-playwright-dotnet)
- [Azure Resource Manager Postgresql Dotnet](#azure-resource-manager-postgresql-dotnet)
- [Azure Resource Manager Redis Dotnet](#azure-resource-manager-redis-dotnet)
- [Azure Resource Manager Sql Dotnet](#azure-resource-manager-sql-dotnet)
- [Azure Search Documents Dotnet](#azure-search-documents-dotnet)
- [Azure Search Documents Py](#azure-search-documents-py)
- [Azure Search Documents Ts](#azure-search-documents-ts)
- [Azure Security Keyvault Keys Dotnet](#azure-security-keyvault-keys-dotnet)
- [Azure Security Keyvault Keys Java](#azure-security-keyvault-keys-java)
- [Azure Security Keyvault Secrets Java](#azure-security-keyvault-secrets-java)
- [Azure Servicebus Dotnet](#azure-servicebus-dotnet)
- [Azure Servicebus Py](#azure-servicebus-py)
- [Azure Servicebus Ts](#azure-servicebus-ts)
- [Azure Speech To Text Rest Py](#azure-speech-to-text-rest-py)
- [Azure Storage Blob Java](#azure-storage-blob-java)
- [Azure Storage Blob Py](#azure-storage-blob-py)
- [Azure Storage Blob Rust](#azure-storage-blob-rust)
- [Azure Storage Blob Ts](#azure-storage-blob-ts)
- [Azure Storage File Datalake Py](#azure-storage-file-datalake-py)
- [Azure Storage File Share Py](#azure-storage-file-share-py)
- [Azure Storage File Share Ts](#azure-storage-file-share-ts)
- [Azure Storage Queue Py](#azure-storage-queue-py)
- [Azure Storage Queue Ts](#azure-storage-queue-ts)
- [Azure Web Pubsub Ts](#azure-web-pubsub-ts)
- [Backend Dev Guidelines](#backend-dev-guidelines)
- [Backtesting Frameworks](#backtesting-frameworks)
- [Bamboohr Automation](#bamboohr-automation)
- [Basecamp Automation](#basecamp-automation)
- [Baseline Ui](#baseline-ui)
- [Bash Defensive Patterns](#bash-defensive-patterns)
- [Bash Linux](#bash-linux)
- [Bash Scripting](#bash-scripting)
- [Bats Testing Patterns](#bats-testing-patterns)
- [Bazel Build Optimization](#bazel-build-optimization)
- [Bdi Mental States](#bdi-mental-states)
- [Bdistill Behavioral Xray](#bdistill-behavioral-xray)
- [Bdistill Knowledge Extraction](#bdistill-knowledge-extraction)
- [Beautiful Prose](#beautiful-prose)
- [Behavioral Modes](#behavioral-modes)
- [Bevy Ecs Expert](#bevy-ecs-expert)
- [Bill Gates](#bill-gates)
- [Billing Automation](#billing-automation)
- [Binary Analysis Patterns](#binary-analysis-patterns)
- [Biopython](#biopython)
- [Bitbucket Automation](#bitbucket-automation)
- [Blockrun](#blockrun)
- [Blog Writing Guide](#blog-writing-guide)
- [Blueprint](#blueprint)
- [Box Automation](#box-automation)
- [Brainstorming](#brainstorming)
- [Brand Guidelines](#brand-guidelines)
- [Brand Guidelines Anthropic](#brand-guidelines-anthropic)
- [Brevo Automation](#brevo-automation)
- [Broken Authentication](#broken-authentication)
- [Browser Automation](#browser-automation)
- [Browser Extension Builder](#browser-extension-builder)
- [Bug Hunter](#bug-hunter)
- [Build](#build)
- [Building Native Ui](#building-native-ui)
- [Bullmq Specialist](#bullmq-specialist)
- [Bun Development](#bun-development)
- [Burp Suite Testing](#burp-suite-testing)
- [Burpsuite Project Parser](#burpsuite-project-parser)
- [C4 Architecture C4 Architecture](#c4-architecture-c4-architecture)
- [C4 Code](#c4-code)
- [C4 Component](#c4-component)
- [C4 Container](#c4-container)
- [C4 Context](#c4-context)
- [Cal Com Automation](#cal-com-automation)
- [Calendly Automation](#calendly-automation)
- [Canva Automation](#canva-automation)
- [Carrier Relationship Management](#carrier-relationship-management)
- [Cc Skill Backend Patterns](#cc-skill-backend-patterns)
- [Cc Skill Clickhouse Io](#cc-skill-clickhouse-io)
- [Cc Skill Coding Standards](#cc-skill-coding-standards)
- [Cc Skill Continuous Learning](#cc-skill-continuous-learning)
- [Cc Skill Frontend Patterns](#cc-skill-frontend-patterns)
- [Cc Skill Project Guidelines Example](#cc-skill-project-guidelines-example)
- [Cc Skill Security Review](#cc-skill-security-review)
- [Cc Skill Strategic Compact](#cc-skill-strategic-compact)
- [Changelog Automation](#changelog-automation)
- [Chat Widget](#chat-widget)
- [Churn Prevention](#churn-prevention)
- [Cicd Automation Workflow Automate](#cicd-automation-workflow-automate)
- [Circleci Automation](#circleci-automation)
- [Cirq](#cirq)
- [Citation Management](#citation-management)
- [Claimable Postgres](#claimable-postgres)
- [Clarity Gate](#clarity-gate)
- [Clarvia Aeo Check](#clarvia-aeo-check)
- [Claude Ally Health](#claude-ally-health)
- [Claude Api](#claude-api)
- [Claude Code Expert](#claude-code-expert)
- [Claude Code Guide](#claude-code-guide)
- [Claude D3Js Skill](#claude-d3js-skill)
- [Claude In Chrome Troubleshooting](#claude-in-chrome-troubleshooting)
- [Claude Monitor](#claude-monitor)
- [Claude Scientific Skills](#claude-scientific-skills)
- [Claude Settings Audit](#claude-settings-audit)
- [Claude Speed Reader](#claude-speed-reader)
- [Claude Win11 Speckit Update Skill](#claude-win11-speckit-update-skill)
- [Clean Code](#clean-code)
- [Clerk Auth](#clerk-auth)
- [Clickup Automation](#clickup-automation)
- [Close Automation](#close-automation)
- [Closed Loop Delivery](#closed-loop-delivery)
- [Cloud Devops](#cloud-devops)
- [Cloud Penetration Testing](#cloud-penetration-testing)
- [Coda Automation](#coda-automation)
- [Code Documentation Code Explain](#code-documentation-code-explain)
- [Code Refactoring Context Restore](#code-refactoring-context-restore)
- [Code Refactoring Tech Debt](#code-refactoring-tech-debt)
- [Code Review Ai Ai Review](#code-review-ai-ai-review)
- [Code Review Checklist](#code-review-checklist)
- [Code Review Excellence](#code-review-excellence)
- [Code Simplifier](#code-simplifier)
- [Codebase Audit Pre Push](#codebase-audit-pre-push)
- [Codebase Cleanup Refactor Clean](#codebase-cleanup-refactor-clean)
- [Codex Review](#codex-review)
- [Cold Email](#cold-email)
- [Comfyui Gateway](#comfyui-gateway)
- [Commit](#commit)
- [Competitive Landscape](#competitive-landscape)
- [Competitor Alternatives](#competitor-alternatives)
- [Computer Use Agents](#computer-use-agents)
- [Computer Vision Expert](#computer-vision-expert)
- [Concise Planning](#concise-planning)
- [Conductor Implement](#conductor-implement)
- [Conductor Manage](#conductor-manage)
- [Conductor New Track](#conductor-new-track)
- [Conductor Revert](#conductor-revert)
- [Conductor Setup](#conductor-setup)
- [Conductor Status](#conductor-status)
- [Conductor Validator](#conductor-validator)
- [Confluence Automation](#confluence-automation)
- [Constant Time Analysis](#constant-time-analysis)
- [Content Creator](#content-creator)
- [Content Strategy](#content-strategy)
- [Context Agent](#context-agent)
- [Context Compression](#context-compression)
- [Context Degradation](#context-degradation)
- [Context Driven Development](#context-driven-development)
- [Context Fundamentals](#context-fundamentals)
- [Context Guardian](#context-guardian)
- [Context Management Context Save](#context-management-context-save)
- [Context Optimization](#context-optimization)
- [Context Window Management](#context-window-management)
- [Context7 Auto Research](#context7-auto-research)
- [Conversation Memory](#conversation-memory)
- [Convertkit Automation](#convertkit-automation)
- [Convex](#convex)
- [Copilot Sdk](#copilot-sdk)
- [Copy Editing](#copy-editing)
- [Copywriting](#copywriting)
- [Core Components](#core-components)
- [Cost Optimization](#cost-optimization)
- [Cpp Pro](#cpp-pro)
- [Cqrs Implementation](#cqrs-implementation)
- [Create Branch](#create-branch)
- [Create Issue Gate](#create-issue-gate)
- [Create Pr](#create-pr)
- [Cred Omega](#cred-omega)
- [Crewai](#crewai)
- [Crypto Bd Agent](#crypto-bd-agent)
- [Customs Trade Compliance](#customs-trade-compliance)
- [Daily](#daily)
- [Daily News Report](#daily-news-report)
- [Data Engineering Data Driven Feature](#data-engineering-data-driven-feature)
- [Data Engineering Data Pipeline](#data-engineering-data-pipeline)
- [Data Quality Frameworks](#data-quality-frameworks)
- [Data Storytelling](#data-storytelling)
- [Data Structure Protocol](#data-structure-protocol)
- [Database](#database)
- [Database Cloud Optimization Cost Optimize](#database-cloud-optimization-cost-optimize)
- [Database Design](#database-design)
- [Database Migration](#database-migration)
- [Database Migrations Migration Observability](#database-migrations-migration-observability)
- [Database Migrations Sql Migrations](#database-migrations-sql-migrations)
- [Datadog Automation](#datadog-automation)
- [Dbos Golang](#dbos-golang)
- [Dbos Python](#dbos-python)
- [Dbos Typescript](#dbos-typescript)
- [Dbt Transformation Patterns](#dbt-transformation-patterns)
- [Ddd Context Mapping](#ddd-context-mapping)
- [Ddd Strategic Design](#ddd-strategic-design)
- [Ddd Tactical Patterns](#ddd-tactical-patterns)
- [Debug Buttercup](#debug-buttercup)
- [Debugging Strategies](#debugging-strategies)
- [Deep Research](#deep-research)
- [Defi Protocol Templates](#defi-protocol-templates)
- [Defuddle](#defuddle)
- [Dependency Management Deps Audit](#dependency-management-deps-audit)
- [Dependency Upgrade](#dependency-upgrade)
- [Deployment Pipeline Design](#deployment-pipeline-design)
- [Deployment Procedures](#deployment-procedures)
- [Deployment Validation Config Validate](#deployment-validation-config-validate)
- [Design Md](#design-md)
- [Design Orchestration](#design-orchestration)
- [Design Spells](#design-spells)
- [Devcontainer Setup](#devcontainer-setup)
- [Development](#development)
- [Devops Deploy](#devops-deploy)
- [Diary](#diary)
- [Differential Review](#differential-review)
- [Discord Automation](#discord-automation)
- [Discord Bot Architect](#discord-bot-architect)
- [Dispatching Parallel Agents](#dispatching-parallel-agents)
- [Distributed Debugging Debug Trace](#distributed-debugging-debug-trace)
- [Distributed Tracing](#distributed-tracing)
- [Django Access Review](#django-access-review)
- [Django Perf Review](#django-perf-review)
- [Doc Coauthoring](#doc-coauthoring)
- [Docker Expert](#docker-expert)
- [Documentation](#documentation)
- [Documentation Generation Doc Generate](#documentation-generation-doc-generate)
- [Documentation Templates](#documentation-templates)
- [Docusign Automation](#docusign-automation)
- [Docx Official](#docx-official)
- [Domain Driven Design](#domain-driven-design)
- [Dotnet Backend](#dotnet-backend)
- [Dotnet Backend Patterns](#dotnet-backend-patterns)
- [Drizzle Orm Expert](#drizzle-orm-expert)
- [Dropbox Automation](#dropbox-automation)
- [E2E Testing](#e2e-testing)
- [E2E Testing Patterns](#e2e-testing-patterns)
- [Earllm Build](#earllm-build)
- [Electron Development](#electron-development)
- [Elon Musk](#elon-musk)
- [Email Sequence](#email-sequence)
- [Email Systems](#email-systems)
- [Embedding Strategies](#embedding-strategies)
- [Emblemai Crypto Wallet](#emblemai-crypto-wallet)
- [Emergency Card](#emergency-card)
- [Employment Contract Templates](#employment-contract-templates)
- [Energy Procurement](#energy-procurement)
- [Enhance Prompt](#enhance-prompt)
- [Environment Setup Guide](#environment-setup-guide)
- [Error Diagnostics Error Analysis](#error-diagnostics-error-analysis)
- [Error Diagnostics Error Trace](#error-diagnostics-error-trace)
- [Error Handling Patterns](#error-handling-patterns)
- [Ethical Hacking Methodology](#ethical-hacking-methodology)
- [Evaluation](#evaluation)
- [Event Sourcing Architect](#event-sourcing-architect)
- [Event Store Design](#event-store-design)
- [Evolution](#evolution)
- [Exa Search](#exa-search)
- [Executing Plans](#executing-plans)
- [Explain Like Socrates](#explain-like-socrates)
- [Expo Api Routes](#expo-api-routes)
- [Expo Cicd Workflows](#expo-cicd-workflows)
- [Expo Deployment](#expo-deployment)
- [Expo Dev Client](#expo-dev-client)
- [Expo Tailwind Setup](#expo-tailwind-setup)
- [Faf Expert](#faf-expert)
- [Faf Wizard](#faf-wizard)
- [Fal Audio](#fal-audio)
- [Fal Generate](#fal-generate)
- [Fal Image Edit](#fal-image-edit)
- [Fal Platform](#fal-platform)
- [Fal Upscale](#fal-upscale)
- [Fal Workflow](#fal-workflow)
- [Family Health Analyzer](#family-health-analyzer)
- [Fastapi Router Py](#fastapi-router-py)
- [Fastapi Templates](#fastapi-templates)
- [Fda Food Safety Auditor](#fda-food-safety-auditor)
- [Fda Medtech Compliance Auditor](#fda-medtech-compliance-auditor)
- [Ffuf Claude Skill](#ffuf-claude-skill)
- [Ffuf Web Fuzzing](#ffuf-web-fuzzing)
- [Figma Automation](#figma-automation)
- [File Organizer](#file-organizer)
- [File Path Traversal](#file-path-traversal)
- [File Uploads](#file-uploads)
- [Filesystem Context](#filesystem-context)
- [Find Bugs](#find-bugs)
- [Finishing A Development Branch](#finishing-a-development-branch)
- [Firebase](#firebase)
- [Firecrawl Scraper](#firecrawl-scraper)
- [Firmware Analyst](#firmware-analyst)
- [Fitness Analyzer](#fitness-analyzer)
- [Fix Review](#fix-review)
- [Fixing Accessibility](#fixing-accessibility)
- [Fixing Motion Performance](#fixing-motion-performance)
- [Flutter Expert](#flutter-expert)
- [Food Database Query](#food-database-query)
- [Form Cro](#form-cro)
- [Fp Async](#fp-async)
- [Fp Backend](#fp-backend)
- [Fp Data Transforms](#fp-data-transforms)
- [Fp Either Ref](#fp-either-ref)
- [Fp Errors](#fp-errors)
- [Fp Option Ref](#fp-option-ref)
- [Fp Pipe Ref](#fp-pipe-ref)
- [Fp Refactor](#fp-refactor)
- [Fp Taskeither Ref](#fp-taskeither-ref)
- [Fp Ts Pragmatic](#fp-ts-pragmatic)
- [Fp Ts React](#fp-ts-react)
- [Fp Types Ref](#fp-types-ref)
- [Framework Migration Code Migrate](#framework-migration-code-migrate)
- [Framework Migration Deps Upgrade](#framework-migration-deps-upgrade)
- [Framework Migration Legacy Modernize](#framework-migration-legacy-modernize)
- [Free Tool Strategy](#free-tool-strategy)
- [Freshdesk Automation](#freshdesk-automation)
- [Freshservice Automation](#freshservice-automation)
- [Frontend Design](#frontend-design)
- [Frontend Dev Guidelines](#frontend-dev-guidelines)
- [Frontend Mobile Development Component Scaffold](#frontend-mobile-development-component-scaffold)
- [Frontend Mobile Security Xss Scan](#frontend-mobile-security-xss-scan)
- [Frontend Slides](#frontend-slides)
- [Frontend Ui Dark Ts](#frontend-ui-dark-ts)
- [Game Development](#game-development)
- [Gcp Cloud Run](#gcp-cloud-run)
- [Gdb Cli](#gdb-cli)
- [Gdpr Data Handling](#gdpr-data-handling)
- [Gemini Api Dev](#gemini-api-dev)
- [Gemini Api Integration](#gemini-api-integration)
- [General](#general)
- [Geo Fundamentals](#geo-fundamentals)
- [Geoffrey Hinton](#geoffrey-hinton)
- [Gh Review Requests](#gh-review-requests)
- [Gha Security Review](#gha-security-review)
- [Git Advanced Workflows](#git-advanced-workflows)
- [Git Hooks Automation](#git-hooks-automation)
- [Git Pr Workflows Git Workflow](#git-pr-workflows-git-workflow)
- [Git Pr Workflows Onboard](#git-pr-workflows-onboard)
- [Git Pr Workflows Pr Enhance](#git-pr-workflows-pr-enhance)
- [Git Pushing](#git-pushing)
- [Github](#github)
- [Github Actions Templates](#github-actions-templates)
- [Github Automation](#github-automation)
- [Github Issue Creator](#github-issue-creator)
- [Github Workflow Automation](#github-workflow-automation)
- [Gitlab Automation](#gitlab-automation)
- [Gitlab Ci Patterns](#gitlab-ci-patterns)
- [Gitops Workflow](#gitops-workflow)
- [Global Chat Agent Discovery](#global-chat-agent-discovery)
- [Gmail Automation](#gmail-automation)
- [Go Concurrency Patterns](#go-concurrency-patterns)
- [Go Playwright](#go-playwright)
- [Go Rod Master](#go-rod-master)
- [Goal Analyzer](#goal-analyzer)
- [Godot 4 Migration](#godot-4-migration)
- [Godot Gdscript Patterns](#godot-gdscript-patterns)
- [Google Analytics Automation](#google-analytics-automation)
- [Google Calendar Automation](#google-calendar-automation)
- [Google Docs Automation](#google-docs-automation)
- [Google Drive Automation](#google-drive-automation)
- [Google Sheets Automation](#google-sheets-automation)
- [Google Slides Automation](#google-slides-automation)
- [Googlesheets Automation](#googlesheets-automation)
- [Grafana Dashboards](#grafana-dashboards)
- [Graphql](#graphql)
- [Growth Engine](#growth-engine)
- [Grpc Golang](#grpc-golang)
- [Health Trend Analyzer](#health-trend-analyzer)
- [Helm Chart Scaffolding](#helm-chart-scaffolding)
- [Helpdesk Automation](#helpdesk-automation)
- [Hierarchical Agent Memory](#hierarchical-agent-memory)
- [Hig Components Content](#hig-components-content)
- [Hig Components Controls](#hig-components-controls)
- [Hig Components Dialogs](#hig-components-dialogs)
- [Hig Components Layout](#hig-components-layout)
- [Hig Components Menus](#hig-components-menus)
- [Hig Components Search](#hig-components-search)
- [Hig Components Status](#hig-components-status)
- [Hig Components System](#hig-components-system)
- [Hig Foundations](#hig-foundations)
- [Hig Inputs](#hig-inputs)
- [Hig Patterns](#hig-patterns)
- [Hig Platforms](#hig-platforms)
- [Hig Project Context](#hig-project-context)
- [Hig Technologies](#hig-technologies)
- [Hono](#hono)
- [Hosted Agents](#hosted-agents)
- [Hosted Agents V2 Py](#hosted-agents-v2-py)
- [Html Injection Testing](#html-injection-testing)
- [Hubspot Automation](#hubspot-automation)
- [Hubspot Integration](#hubspot-integration)
- [Hugging Face Community Evals](#hugging-face-community-evals)
- [Hugging Face Dataset Viewer](#hugging-face-dataset-viewer)
- [Hugging Face Gradio](#hugging-face-gradio)
- [Hugging Face Jobs](#hugging-face-jobs)
- [Hugging Face Model Trainer](#hugging-face-model-trainer)
- [Hugging Face Paper Publisher](#hugging-face-paper-publisher)
- [Hugging Face Papers](#hugging-face-papers)
- [Hugging Face Tool Builder](#hugging-face-tool-builder)
- [Hugging Face Trackio](#hugging-face-trackio)
- [Hugging Face Vision Trainer](#hugging-face-vision-trainer)
- [Humanize Chinese](#humanize-chinese)
- [Hybrid Cloud Networking](#hybrid-cloud-networking)
- [Hybrid Search Implementation](#hybrid-search-implementation)
- [I18N Localization](#i18n-localization)
- [Iconsax Library](#iconsax-library)
- [Idea Darwin](#idea-darwin)
- [Idor Testing](#idor-testing)
- [Ilya Sutskever](#ilya-sutskever)
- [Image Studio](#image-studio)
- [Imagen](#imagen)
- [Incident Response Smart Fix](#incident-response-smart-fix)
- [Incident Runbook Templates](#incident-runbook-templates)
- [Infinite Gratitude](#infinite-gratitude)
- [Inngest](#inngest)
- [Instagram](#instagram)
- [Instagram Automation](#instagram-automation)
- [Interactive Portfolio](#interactive-portfolio)
- [Intercom Automation](#intercom-automation)
- [Internal Comms](#internal-comms)
- [Interview Coach](#interview-coach)
- [Inventory Demand Planning](#inventory-demand-planning)
- [Ios Debugger Agent](#ios-debugger-agent)
- [Istio Traffic Management](#istio-traffic-management)
- [Iterate Pr](#iterate-pr)
- [Javascript Mastery](#javascript-mastery)
- [Javascript Testing Patterns](#javascript-testing-patterns)
- [Javascript Typescript Typescript Scaffold](#javascript-typescript-typescript-scaffold)
- [Jira Automation](#jira-automation)
- [Jobgpt](#jobgpt)
- [Jq](#jq)
- [Json Canvas](#json-canvas)
- [Junta Leiloeiros](#junta-leiloeiros)
- [K6 Load Testing](#k6-load-testing)
- [K8S Manifest Generator](#k8s-manifest-generator)
- [K8S Security Policies](#k8s-security-policies)
- [Kaizen](#kaizen)
- [Keyword Extractor](#keyword-extractor)
- [Klaviyo Automation](#klaviyo-automation)
- [Kotlin Coroutines Expert](#kotlin-coroutines-expert)
- [Kpi Dashboard Design](#kpi-dashboard-design)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Landing Page Generator](#landing-page-generator)
- [Langchain Architecture](#langchain-architecture)
- [Langfuse](#langfuse)
- [Langgraph](#langgraph)
- [Laravel Expert](#laravel-expert)
- [Laravel Security Audit](#laravel-security-audit)
- [Last30Days](#last30days)
- [Latex Paper Conversion](#latex-paper-conversion)
- [Launch Strategy](#launch-strategy)
- [Lead Magnets](#lead-magnets)
- [Leiloeiro Avaliacao](#leiloeiro-avaliacao)
- [Leiloeiro Edital](#leiloeiro-edital)
- [Leiloeiro Ia](#leiloeiro-ia)
- [Leiloeiro Juridico](#leiloeiro-juridico)
- [Leiloeiro Mercado](#leiloeiro-mercado)
- [Leiloeiro Risco](#leiloeiro-risco)
- [Lex](#lex)
- [Libreoffice](#libreoffice)
- [Linear Automation](#linear-automation)
- [Linear Claude Skill](#linear-claude-skill)
- [Linkedin Automation](#linkedin-automation)
- [Linkedin Cli](#linkedin-cli)
- [Linkerd Patterns](#linkerd-patterns)
- [Lint And Validate](#lint-and-validate)
- [Linux Privilege Escalation](#linux-privilege-escalation)
- [Linux Shell Scripting](#linux-shell-scripting)
- [Linux Troubleshooting](#linux-troubleshooting)
- [Llm App Patterns](#llm-app-patterns)
- [Llm Application Dev Ai Assistant](#llm-application-dev-ai-assistant)
- [Llm Application Dev Langchain Agent](#llm-application-dev-langchain-agent)
- [Llm Application Dev Prompt Optimize](#llm-application-dev-prompt-optimize)
- [Llm Evaluation](#llm-evaluation)
- [Llm Ops](#llm-ops)
- [Llm Prompt Optimizer](#llm-prompt-optimizer)
- [Llm Structured Output](#llm-structured-output)
- [Local Legal Seo Audit](#local-legal-seo-audit)
- [Logistics Exception Management](#logistics-exception-management)
- [Loki Mode](#loki-mode)
- [M365 Agents Dotnet](#m365-agents-dotnet)
- [M365 Agents Py](#m365-agents-py)
- [M365 Agents Ts](#m365-agents-ts)
- [Machine Learning Ops Ml Pipeline](#machine-learning-ops-ml-pipeline)
- [Macos Menubar Tuist App](#macos-menubar-tuist-app)
- [Macos Spm App Packaging](#macos-spm-app-packaging)
- [Magic Animator](#magic-animator)
- [Magic Ui Generator](#magic-ui-generator)
- [Mailchimp Automation](#mailchimp-automation)
- [Make Automation](#make-automation)
- [Makepad Animation](#makepad-animation)
- [Makepad Basics](#makepad-basics)
- [Makepad Deployment](#makepad-deployment)
- [Makepad Dsl](#makepad-dsl)
- [Makepad Event Action](#makepad-event-action)
- [Makepad Font](#makepad-font)
- [Makepad Layout](#makepad-layout)
- [Makepad Platform](#makepad-platform)
- [Makepad Reference](#makepad-reference)
- [Makepad Shaders](#makepad-shaders)
- [Makepad Skills](#makepad-skills)
- [Makepad Splash](#makepad-splash)
- [Makepad Widgets](#makepad-widgets)
- [Malware Analyst](#malware-analyst)
- [Manage Skills](#manage-skills)
- [Manifest](#manifest)
- [Market Sizing Analysis](#market-sizing-analysis)
- [Marketing Ideas](#marketing-ideas)
- [Marketing Psychology](#marketing-psychology)
- [Matematico Tao](#matematico-tao)
- [Matplotlib](#matplotlib)
- [Maxia](#maxia)
- [Mcp Builder](#mcp-builder)
- [Mcp Builder Ms](#mcp-builder-ms)
- [Memory Forensics](#memory-forensics)
- [Memory Safety Patterns](#memory-safety-patterns)
- [Memory Systems](#memory-systems)
- [Mental Health Analyzer](#mental-health-analyzer)
- [Metasploit Framework](#metasploit-framework)
- [Micro Saas Launcher](#micro-saas-launcher)
- [Microservices Patterns](#microservices-patterns)
- [Microsoft Azure Webjobs Extensions Authentication Events Dotnet](#microsoft-azure-webjobs-extensions-authentication-events-dotnet)
- [Microsoft Teams Automation](#microsoft-teams-automation)
- [Miro Automation](#miro-automation)
- [Mixpanel Automation](#mixpanel-automation)
- [Ml Pipeline Workflow](#ml-pipeline-workflow)
- [Mobile Design](#mobile-design)
- [Modern Javascript Patterns](#modern-javascript-patterns)
- [Molykit](#molykit)
- [Monday Automation](#monday-automation)
- [Monetization](#monetization)
- [Monorepo Architect](#monorepo-architect)
- [Monorepo Management](#monorepo-management)
- [Monte Carlo Monitor Creation](#monte-carlo-monitor-creation)
- [Monte Carlo Prevent](#monte-carlo-prevent)
- [Monte Carlo Push Ingestion](#monte-carlo-push-ingestion)
- [Monte Carlo Validation Notebook](#monte-carlo-validation-notebook)
- [Moodle External Api Development](#moodle-external-api-development)
- [Moyu](#moyu)
- [Mtls Configuration](#mtls-configuration)
- [Multi Advisor](#multi-advisor)
- [Multi Agent Brainstorming](#multi-agent-brainstorming)
- [Multi Agent Patterns](#multi-agent-patterns)
- [Multi Agent Task Orchestrator](#multi-agent-task-orchestrator)
- [Multi Cloud Architecture](#multi-cloud-architecture)
- [Multi Platform Apps Multi Platform](#multi-platform-apps-multi-platform)
- [N8N Code Javascript](#n8n-code-javascript)
- [N8N Code Python](#n8n-code-python)
- [N8N Expression Syntax](#n8n-expression-syntax)
- [N8N Mcp Tools Expert](#n8n-mcp-tools-expert)
- [N8N Node Configuration](#n8n-node-configuration)
- [N8N Validation Expert](#n8n-validation-expert)
- [N8N Workflow Patterns](#n8n-workflow-patterns)
- [Nanobanana Ppt Skills](#nanobanana-ppt-skills)
- [Native Data Fetching](#native-data-fetching)
- [Neon Postgres](#neon-postgres)
- [Nerdzao Elite](#nerdzao-elite)
- [Nerdzao Elite Gemini High](#nerdzao-elite-gemini-high)
- [Nestjs Expert](#nestjs-expert)
- [Network 101](#network-101)
- [Networkx](#networkx)
- [New Rails Project](#new-rails-project)
- [Nextjs App Router Patterns](#nextjs-app-router-patterns)
- [Nextjs Best Practices](#nextjs-best-practices)
- [Nextjs Supabase Auth](#nextjs-supabase-auth)
- [Nft Standards](#nft-standards)
- [Nodejs Backend Patterns](#nodejs-backend-patterns)
- [Nodejs Best Practices](#nodejs-best-practices)
- [Nosql Expert](#nosql-expert)
- [Notebooklm](#notebooklm)
- [Notion Automation](#notion-automation)
- [Notion Template Business](#notion-template-business)
- [Nutrition Analyzer](#nutrition-analyzer)
- [Nx Workspace Patterns](#nx-workspace-patterns)
- [Observability Monitoring Monitor Setup](#observability-monitoring-monitor-setup)
- [Observability Monitoring Slo Implement](#observability-monitoring-slo-implement)
- [Obsidian Bases](#obsidian-bases)
- [Obsidian Cli](#obsidian-cli)
- [Obsidian Clipper Template Creator](#obsidian-clipper-template-creator)
- [Obsidian Markdown](#obsidian-markdown)
- [Occupational Health Analyzer](#occupational-health-analyzer)
- [Odoo Accounting Setup](#odoo-accounting-setup)
- [Odoo Automated Tests](#odoo-automated-tests)
- [Odoo Backup Strategy](#odoo-backup-strategy)
- [Odoo Docker Deployment](#odoo-docker-deployment)
- [Odoo Ecommerce Configurator](#odoo-ecommerce-configurator)
- [Odoo Edi Connector](#odoo-edi-connector)
- [Odoo Hr Payroll Setup](#odoo-hr-payroll-setup)
- [Odoo Inventory Optimizer](#odoo-inventory-optimizer)
- [Odoo L10N Compliance](#odoo-l10n-compliance)
- [Odoo Manufacturing Advisor](#odoo-manufacturing-advisor)
- [Odoo Migration Helper](#odoo-migration-helper)
- [Odoo Module Developer](#odoo-module-developer)
- [Odoo Orm Expert](#odoo-orm-expert)
- [Odoo Performance Tuner](#odoo-performance-tuner)
- [Odoo Project Timesheet](#odoo-project-timesheet)
- [Odoo Purchase Workflow](#odoo-purchase-workflow)
- [Odoo Qweb Templates](#odoo-qweb-templates)
- [Odoo Rpc Api](#odoo-rpc-api)
- [Odoo Sales Crm Expert](#odoo-sales-crm-expert)
- [Odoo Security Rules](#odoo-security-rules)
- [Odoo Shopify Integration](#odoo-shopify-integration)
- [Odoo Upgrade Advisor](#odoo-upgrade-advisor)
- [Odoo Woocommerce Bridge](#odoo-woocommerce-bridge)
- [Odoo Xml Views Builder](#odoo-xml-views-builder)
- [Office Productivity](#office-productivity)
- [On Call Handoff Patterns](#on-call-handoff-patterns)
- [Onboarding Cro](#onboarding-cro)
- [One Drive Automation](#one-drive-automation)
- [Openapi Spec Generation](#openapi-spec-generation)
- [Openclaw Github Repo Commander](#openclaw-github-repo-commander)
- [Oral Health Analyzer](#oral-health-analyzer)
- [Orchestrate Batch Refactor](#orchestrate-batch-refactor)
- [Os Scripting](#os-scripting)
- [Oss Hunter](#oss-hunter)
- [Outlook Automation](#outlook-automation)
- [Outlook Calendar Automation](#outlook-calendar-automation)
- [Page Cro](#page-cro)
- [Pagerduty Automation](#pagerduty-automation)
- [Paid Ads](#paid-ads)
- [Pakistan Payments Stack](#pakistan-payments-stack)
- [Parallel Agents](#parallel-agents)
- [Paypal Integration](#paypal-integration)
- [Paywall Upgrade Cro](#paywall-upgrade-cro)
- [Pci Compliance](#pci-compliance)
- [Pdf Official](#pdf-official)
- [Pentest Checklist](#pentest-checklist)
- [Pentest Commands](#pentest-commands)
- [Performance Optimizer](#performance-optimizer)
- [Performance Profiling](#performance-profiling)
- [Performance Testing Review Multi Agent Review](#performance-testing-review-multi-agent-review)
- [Personal Tool Builder](#personal-tool-builder)
- [Phase Gated Debugging](#phase-gated-debugging)
- [Pipecat Friday Agent](#pipecat-friday-agent)
- [Pipedrive Automation](#pipedrive-automation)
- [Plaid Fintech](#plaid-fintech)
- [Plan Writing](#plan-writing)
- [Planning With Files](#planning-with-files)
- [Playwright Java](#playwright-java)
- [Playwright Skill](#playwright-skill)
- [Plotly](#plotly)
- [Podcast Generation](#podcast-generation)
- [Polars](#polars)
- [Popup Cro](#popup-cro)
- [Postgres Best Practices](#postgres-best-practices)
- [Postgresql](#postgresql)
- [Postgresql Optimization](#postgresql-optimization)
- [Posthog Automation](#posthog-automation)
- [Postmark Automation](#postmark-automation)
- [Postmortem Writing](#postmortem-writing)
- [Powershell Windows](#powershell-windows)
- [Pptx Official](#pptx-official)
- [Pr Writer](#pr-writer)
- [Pricing Strategy](#pricing-strategy)
- [Prisma Expert](#prisma-expert)
- [Privacy By Design](#privacy-by-design)
- [Privilege Escalation Methods](#privilege-escalation-methods)
- [Product Design](#product-design)
- [Product Inventor](#product-inventor)
- [Product Manager](#product-manager)
- [Product Manager Toolkit](#product-manager-toolkit)
- [Product Marketing Context](#product-marketing-context)
- [Production Code Audit](#production-code-audit)
- [Production Scheduling](#production-scheduling)
- [Professional Proofreader](#professional-proofreader)
- [Programmatic Seo](#programmatic-seo)
- [Progressive Estimation](#progressive-estimation)
- [Progressive Web App](#progressive-web-app)
- [Project Development](#project-development)
- [Project Skill Audit](#project-skill-audit)
- [Projection Patterns](#projection-patterns)
- [Prometheus Configuration](#prometheus-configuration)
- [Prompt Caching](#prompt-caching)
- [Prompt Engineering](#prompt-engineering)
- [Prompt Engineering Patterns](#prompt-engineering-patterns)
- [Prompt Library](#prompt-library)
- [Protect Mcp Governance](#protect-mcp-governance)
- [Protocol Reverse Engineering](#protocol-reverse-engineering)
- [Pubmed Database](#pubmed-database)
- [Pydantic Ai](#pydantic-ai)
- [Pydantic Models Py](#pydantic-models-py)
- [Pypict Skill](#pypict-skill)
- [Python Development Python Scaffold](#python-development-python-scaffold)
- [Python Fastapi Development](#python-fastapi-development)
- [Python Packaging](#python-packaging)
- [Python Patterns](#python-patterns)
- [Python Performance Optimization](#python-performance-optimization)
- [Python Pptx Generator](#python-pptx-generator)
- [Python Testing Patterns](#python-testing-patterns)
- [Qiskit](#qiskit)
- [Quality Nonconformance](#quality-nonconformance)
- [Radix Ui Design System](#radix-ui-design-system)
- [Rag Engineer](#rag-engineer)
- [Rag Implementation](#rag-implementation)
- [React Best Practices](#react-best-practices)
- [React Component Performance](#react-component-performance)
- [React Flow Architect](#react-flow-architect)
- [React Flow Node Ts](#react-flow-node-ts)
- [React Modernization](#react-modernization)
- [React Native Architecture](#react-native-architecture)
- [React Nextjs Development](#react-nextjs-development)
- [React State Management](#react-state-management)
- [React Ui Patterns](#react-ui-patterns)
- [Readme](#readme)
- [Recallmax](#recallmax)
- [Receiving Code Review](#receiving-code-review)
- [Red Team Tactics](#red-team-tactics)
- [Red Team Tools](#red-team-tools)
- [Reddit Automation](#reddit-automation)
- [Referral Program](#referral-program)
- [Rehabilitation Analyzer](#rehabilitation-analyzer)
- [Remotion](#remotion)
- [Remotion Best Practices](#remotion-best-practices)
- [Render Automation](#render-automation)
- [Requesting Code Review](#requesting-code-review)
- [Returns Reverse Logistics](#returns-reverse-logistics)
- [Reverse Engineer](#reverse-engineer)
- [Revops](#revops)
- [Risk Metrics Calculation](#risk-metrics-calculation)
- [Robius App Architecture](#robius-app-architecture)
- [Robius Event Action](#robius-event-action)
- [Robius Matrix Integration](#robius-matrix-integration)
- [Robius State Management](#robius-state-management)
- [Robius Widget Patterns](#robius-widget-patterns)
- [Rust Async Patterns](#rust-async-patterns)
- [Saas Multi Tenant](#saas-multi-tenant)
- [Saas Mvp Launcher](#saas-mvp-launcher)
- [Saga Orchestration](#saga-orchestration)
- [Sales Enablement](#sales-enablement)
- [Salesforce Automation](#salesforce-automation)
- [Salesforce Development](#salesforce-development)
- [Sam Altman](#sam-altman)
- [Sankhya Dashboard Html Jsp Custom Best Pratices](#sankhya-dashboard-html-jsp-custom-best-pratices)
- [Sast Configuration](#sast-configuration)
- [Satori](#satori)
- [Scanning Tools](#scanning-tools)
- [Scanpy](#scanpy)
- [Schema Markup](#schema-markup)
- [Scientific Writing](#scientific-writing)
- [Scikit Learn](#scikit-learn)
- [Screen Reader Testing](#screen-reader-testing)
- [Screenshots](#screenshots)
- [Scroll Experience](#scroll-experience)
- [Seaborn](#seaborn)
- [Secrets Management](#secrets-management)
- [Security](#security)
- [Security Audit](#security-audit)
- [Security Bluebook Builder](#security-bluebook-builder)
- [Security Compliance Compliance Check](#security-compliance-compliance-check)
- [Security Requirement Extraction](#security-requirement-extraction)
- [Security Scanning Security Dependencies](#security-scanning-security-dependencies)
- [Security Scanning Security Sast](#security-scanning-security-sast)
- [Seek And Analyze Video](#seek-and-analyze-video)
- [Segment Automation](#segment-automation)
- [Segment Cdp](#segment-cdp)
- [Semgrep Rule Creator](#semgrep-rule-creator)
- [Semgrep Rule Variant Creator](#semgrep-rule-variant-creator)
- [Sendgrid Automation](#sendgrid-automation)
- [Senior Architect](#senior-architect)
- [Senior Frontend](#senior-frontend)
- [Senior Fullstack](#senior-fullstack)
- [Sentry Automation](#sentry-automation)
- [Seo](#seo)
- [Seo Aeo Blog Writer](#seo-aeo-blog-writer)
- [Seo Aeo Content Cluster](#seo-aeo-content-cluster)
- [Seo Aeo Content Quality Auditor](#seo-aeo-content-quality-auditor)
- [Seo Aeo Internal Linking](#seo-aeo-internal-linking)
- [Seo Aeo Keyword Research](#seo-aeo-keyword-research)
- [Seo Aeo Landing Page Writer](#seo-aeo-landing-page-writer)
- [Seo Aeo Meta Description Generator](#seo-aeo-meta-description-generator)
- [Seo Aeo Schema Generator](#seo-aeo-schema-generator)
- [Seo Audit](#seo-audit)
- [Seo Competitor Pages](#seo-competitor-pages)
- [Seo Content](#seo-content)
- [Seo Dataforseo](#seo-dataforseo)
- [Seo Forensic Incident Response](#seo-forensic-incident-response)
- [Seo Fundamentals](#seo-fundamentals)
- [Seo Geo](#seo-geo)
- [Seo Hreflang](#seo-hreflang)
- [Seo Image Gen](#seo-image-gen)
- [Seo Images](#seo-images)
- [Seo Page](#seo-page)
- [Seo Plan](#seo-plan)
- [Seo Programmatic](#seo-programmatic)
- [Seo Schema](#seo-schema)
- [Seo Sitemap](#seo-sitemap)
- [Seo Technical](#seo-technical)
- [Server Management](#server-management)
- [Service Mesh Expert](#service-mesh-expert)
- [Service Mesh Observability](#service-mesh-observability)
- [Sexual Health Analyzer](#sexual-health-analyzer)
- [Shadcn](#shadcn)
- [Shader Programming Glsl](#shader-programming-glsl)
- [Sharp Edges](#sharp-edges)
- [Shellcheck Configuration](#shellcheck-configuration)
- [Shodan Reconnaissance](#shodan-reconnaissance)
- [Shopify Apps](#shopify-apps)
- [Shopify Automation](#shopify-automation)
- [Shopify Development](#shopify-development)
- [Signup Flow Cro](#signup-flow-cro)
- [Similarity Search Patterns](#similarity-search-patterns)
- [Simplify Code](#simplify-code)
- [Site Architecture](#site-architecture)
- [Skill Check](#skill-check)
- [Skill Creator](#skill-creator)
- [Skill Creator Ms](#skill-creator-ms)
- [Skill Developer](#skill-developer)
- [Skill Improver](#skill-improver)
- [Skill Installer](#skill-installer)
- [Skill Rails Upgrade](#skill-rails-upgrade)
- [Skill Router](#skill-router)
- [Skill Scanner](#skill-scanner)
- [Skill Seekers](#skill-seekers)
- [Skill Sentinel](#skill-sentinel)
- [Skill Writer](#skill-writer)
- [Skin Health Analyzer](#skin-health-analyzer)
- [Slack Automation](#slack-automation)
- [Slack Bot Builder](#slack-bot-builder)
- [Slack Gif Creator](#slack-gif-creator)
- [Sleep Analyzer](#sleep-analyzer)
- [Slo Implementation](#slo-implementation)
- [Smtp Penetration Testing](#smtp-penetration-testing)
- [Snowflake Development](#snowflake-development)
- [Social Content](#social-content)
- [Social Orchestrator](#social-orchestrator)
- [Software Architecture](#software-architecture)
- [Solidity Security](#solidity-security)
- [Spark Optimization](#spark-optimization)
- [Spdd](#spdd)
- [Spec To Code Compliance](#spec-to-code-compliance)
- [Speckit Updater](#speckit-updater)
- [Speed](#speed)
- [Spline 3D Integration](#spline-3d-integration)
- [Sql Injection Testing](#sql-injection-testing)
- [Sql Optimization Patterns](#sql-optimization-patterns)
- [Sqlmap Database Pentesting](#sqlmap-database-pentesting)
- [Square Automation](#square-automation)
- [Sred Project Organizer](#sred-project-organizer)
- [Sred Work Summary](#sred-work-summary)
- [Ssh Penetration Testing](#ssh-penetration-testing)
- [Stability Ai](#stability-ai)
- [Startup Business Analyst Business Case](#startup-business-analyst-business-case)
- [Startup Business Analyst Financial Projections](#startup-business-analyst-financial-projections)
- [Startup Business Analyst Market Opportunity](#startup-business-analyst-market-opportunity)
- [Startup Financial Modeling](#startup-financial-modeling)
- [Startup Metrics Framework](#startup-metrics-framework)
- [Statsmodels](#statsmodels)
- [Steve Jobs](#steve-jobs)
- [Stitch Loop](#stitch-loop)
- [Stitch Ui Design](#stitch-ui-design)
- [Stride Analysis Patterns](#stride-analysis-patterns)
- [Stripe Automation](#stripe-automation)
- [Stripe Integration](#stripe-integration)
- [Subagent Driven Development](#subagent-driven-development)
- [Supabase Automation](#supabase-automation)
- [Superpowers Lab](#superpowers-lab)
- [Supply Chain Risk Auditor](#supply-chain-risk-auditor)
- [Sveltekit](#sveltekit)
- [Swift Concurrency Expert](#swift-concurrency-expert)
- [Swiftui Expert Skill](#swiftui-expert-skill)
- [Swiftui Liquid Glass](#swiftui-liquid-glass)
- [Swiftui Performance Audit](#swiftui-performance-audit)
- [Swiftui Ui Patterns](#swiftui-ui-patterns)
- [Swiftui View Refactor](#swiftui-view-refactor)
- [Sympy](#sympy)
- [Systematic Debugging](#systematic-debugging)
- [Systems Programming Rust Project](#systems-programming-rust-project)
- [Tailwind Design System](#tailwind-design-system)
- [Tailwind Patterns](#tailwind-patterns)
- [Tanstack Query Expert](#tanstack-query-expert)
- [Task Intelligence](#task-intelligence)
- [Tavily Web](#tavily-web)
- [Tcm Constitution Analyzer](#tcm-constitution-analyzer)
- [Tdd Workflow](#tdd-workflow)
- [Tdd Workflows Tdd Green](#tdd-workflows-tdd-green)
- [Team Collaboration Issue](#team-collaboration-issue)
- [Team Collaboration Standup Notes](#team-collaboration-standup-notes)
- [Team Composition Analysis](#team-composition-analysis)
- [Technical Change Tracker](#technical-change-tracker)
- [Telegram](#telegram)
- [Telegram Automation](#telegram-automation)
- [Telegram Bot Builder](#telegram-bot-builder)
- [Telegram Mini App](#telegram-mini-app)
- [Temporal Golang Pro](#temporal-golang-pro)
- [Temporal Python Testing](#temporal-python-testing)
- [Terraform Aws Modules](#terraform-aws-modules)
- [Terraform Infrastructure](#terraform-infrastructure)
- [Terraform Module Library](#terraform-module-library)
- [Terraform Skill](#terraform-skill)
- [Test Driven Development](#test-driven-development)
- [Test Fixing](#test-fixing)
- [Testing Patterns](#testing-patterns)
- [Testing Qa](#testing-qa)
- [Theme Factory](#theme-factory)
- [Threat Mitigation Mapping](#threat-mitigation-mapping)
- [Threat Modeling Expert](#threat-modeling-expert)
- [Threejs Animation](#threejs-animation)
- [Threejs Fundamentals](#threejs-fundamentals)
- [Threejs Geometry](#threejs-geometry)
- [Threejs Interaction](#threejs-interaction)
- [Threejs Lighting](#threejs-lighting)
- [Threejs Loaders](#threejs-loaders)
- [Threejs Materials](#threejs-materials)
- [Threejs Postprocessing](#threejs-postprocessing)
- [Threejs Shaders](#threejs-shaders)
- [Threejs Skills](#threejs-skills)
- [Threejs Textures](#threejs-textures)
- [Tiktok Automation](#tiktok-automation)
- [Tmux](#tmux)
- [Todoist Automation](#todoist-automation)
- [Tool Design](#tool-design)
- [Tool Use Guardian](#tool-use-guardian)
- [Top Web Vulnerabilities](#top-web-vulnerabilities)
- [Track Management](#track-management)
- [Transformers Js](#transformers-js)
- [Travel Health Analyzer](#travel-health-analyzer)
- [Trello Automation](#trello-automation)
- [Trigger Dev](#trigger-dev)
- [Trpc Fullstack](#trpc-fullstack)
- [Turborepo Caching](#turborepo-caching)
- [Twilio Communications](#twilio-communications)
- [Twitter Automation](#twitter-automation)
- [Typescript Advanced Types](#typescript-advanced-types)
- [Typescript Expert](#typescript-expert)
- [Ui A11Y](#ui-a11y)
- [Ui Component](#ui-component)
- [Ui Page](#ui-page)
- [Ui Pattern](#ui-pattern)
- [Ui Review](#ui-review)
- [Ui Setup](#ui-setup)
- [Ui Skills](#ui-skills)
- [Ui Tokens](#ui-tokens)
- [Ui Ux Pro Max](#ui-ux-pro-max)
- [Uncle Bob Craft](#uncle-bob-craft)
- [Uniprot Database](#uniprot-database)
- [Unit Testing Test Generate](#unit-testing-test-generate)
- [Unity Ecs Patterns](#unity-ecs-patterns)
- [Unreal Engine Cpp Pro](#unreal-engine-cpp-pro)
- [Unsplash Integration](#unsplash-integration)
- [Upgrading Expo](#upgrading-expo)
- [Upstash Qstash](#upstash-qstash)
- [Using Git Worktrees](#using-git-worktrees)
- [Using Neon](#using-neon)
- [Using Superpowers](#using-superpowers)
- [Uv Package Manager](#uv-package-manager)
- [Ux Audit](#ux-audit)
- [Ux Copy](#ux-copy)
- [Ux Feedback](#ux-feedback)
- [Ux Flow](#ux-flow)
- [Uxui Principles](#uxui-principles)
- [Variant Analysis](#variant-analysis)
- [Varlock](#varlock)
- [Varlock Claude Skill](#varlock-claude-skill)
- [Vector Database Engineer](#vector-database-engineer)
- [Vector Index Tuning](#vector-index-tuning)
- [Vercel Ai Sdk Expert](#vercel-ai-sdk-expert)
- [Vercel Automation](#vercel-automation)
- [Vercel Deployment](#vercel-deployment)
- [Verification Before Completion](#verification-before-completion)
- [Vexor](#vexor)
- [Vexor Cli](#vexor-cli)
- [Vibe Code Auditor](#vibe-code-auditor)
- [Vibers Code Review](#vibers-code-review)
- [Viboscope](#viboscope)
- [Videodb](#videodb)
- [Videodb Skills](#videodb-skills)
- [Viral Generator Builder](#viral-generator-builder)
- [Vizcom](#vizcom)
- [Voice Agents](#voice-agents)
- [Voice Ai Development](#voice-ai-development)
- [Voice Ai Engine Development](#voice-ai-engine-development)
- [Vulnerability Scanner](#vulnerability-scanner)
- [Warren Buffett](#warren-buffett)
- [Wcag Audit Patterns](#wcag-audit-patterns)
- [Web Artifacts Builder](#web-artifacts-builder)
- [Web Design Guidelines](#web-design-guidelines)
- [Web Performance Optimization](#web-performance-optimization)
- [Web Scraper](#web-scraper)
- [Web Security Testing](#web-security-testing)
- [Web3 Testing](#web3-testing)
- [Webapp Testing](#webapp-testing)
- [Webflow Automation](#webflow-automation)
- [Weightloss Analyzer](#weightloss-analyzer)
- [Wellally Tech](#wellally-tech)
- [Whatsapp Automation](#whatsapp-automation)
- [Whatsapp Cloud Api](#whatsapp-cloud-api)
- [Wiki Architect](#wiki-architect)
- [Wiki Changelog](#wiki-changelog)
- [Wiki Onboarding](#wiki-onboarding)
- [Wiki Page Writer](#wiki-page-writer)
- [Wiki Qa](#wiki-qa)
- [Wiki Researcher](#wiki-researcher)
- [Wiki Vitepress](#wiki-vitepress)
- [Windows Privilege Escalation](#windows-privilege-escalation)
- [Windows Shell Reliability](#windows-shell-reliability)
- [Wireshark Analysis](#wireshark-analysis)
- [Wordpress](#wordpress)
- [Wordpress Penetration Testing](#wordpress-penetration-testing)
- [Wordpress Plugin Development](#wordpress-plugin-development)
- [Wordpress Theme Development](#wordpress-theme-development)
- [Wordpress Woocommerce Development](#wordpress-woocommerce-development)
- [Workflow Orchestration Patterns](#workflow-orchestration-patterns)
- [Workflow Patterns](#workflow-patterns)
- [Wrike Automation](#wrike-automation)
- [Writing Plans](#writing-plans)
- [Writing Skills](#writing-skills)
- [X Article Publisher Skill](#x-article-publisher-skill)
- [X Twitter Scraper](#x-twitter-scraper)
- [Xlsx Official](#xlsx-official)
- [Xss Html Injection](#xss-html-injection)
- [Xvary Stock Research](#xvary-stock-research)
- [Yann Lecun](#yann-lecun)
- [Yann Lecun Debate](#yann-lecun-debate)
- [Yann Lecun Filosofia](#yann-lecun-filosofia)
- [Yann Lecun Tecnico](#yann-lecun-tecnico)
- [Yes Md](#yes-md)
- [Youtube Automation](#youtube-automation)
- [Youtube Summarizer](#youtube-summarizer)
- [Zapier Make Patterns](#zapier-make-patterns)
- [Zendesk Automation](#zendesk-automation)
- [Zeroize Audit](#zeroize-audit)
- [Zod Validation Expert](#zod-validation-expert)
- [Zoho Crm Automation](#zoho-crm-automation)
- [Zoom Automation](#zoom-automation)
- [Zustand Store Ts](#zustand-store-ts)

### 00 Andruia Consultant
- **🤖 Andru.ia Solutions Architect - Hybrid Engine (v2.0) (@🤖-andru.ia-solutions-architect---hybrid-engine-(v2.0))**: ---

### 007
- **007 — Licenca para Auditar (@007-—-licenca-para-auditar)**: ---
- **AI Agent & LLM Pipeline Security Guide (@ai-agent-&-llm-pipeline-security-guide)**: > Security patterns, attacks, and defenses for AI agents, LLM applications, and prompt pipelines.
- **API Security Patterns & Anti-Patterns (@api-security-patterns-&-anti-patterns)**: > Reference for securing REST APIs, webhooks, and service-to-service communication.
- **Incident Response Playbooks (@incident-response-playbooks)**: > Extended playbooks for common security incidents.
- **OWASP Top 10 Checklists (@owasp-top-10-checklists)**: > Quick-reference checklists for the three most relevant OWASP Top 10 lists.
- **STRIDE & PASTA Threat Modeling Guide (@stride-&-pasta-threat-modeling-guide)**: > Practical guide for threat modeling systems, APIs, and AI agents.

### 10 Andruia Skill Smith
- **🔨 Andru.ia Skill-Smith (The Forge) (@🔨-andru.ia-skill-smith-(the-forge))**: ---

### 20 Andruia Niche Intelligence
- **🧠 Andru.ia Niche Intelligence (Dominio Experto) (@🧠-andru.ia-niche-intelligence-(dominio-experto))**: ---

### 3D Web Experience
- **3D Web Experience (@3d-web-experience)**: ---

### Ab Test Setup
- **A/B Test Setup (@a/b-test-setup)**: ---

### Acceptance Orchestrator
- **Acceptance Orchestrator (@acceptance-orchestrator)**: ---

### Accessibility Compliance Accessibility Audit
- **Accessibility Audit and Testing (@accessibility-audit-and-testing)**: ---
- **Accessibility Audit and Testing Implementation Playbook (@accessibility-audit-and-testing-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Active Directory Attacks
- **Active Directory Attacks (@active-directory-attacks)**: ---
- **Advanced Active Directory Attacks Reference (@advanced-active-directory-attacks-reference)**: 1. [Delegation Attacks](#delegation-attacks)

### Activecampaign Automation
- **ActiveCampaign Automation via Rube MCP (@activecampaign-automation-via-rube-mcp)**: ---

### Ad Creative
- **Ad Creative (@ad-creative)**: ---
- **Generative AI Tools for Ad Creative (@generative-ai-tools-for-ad-creative)**: Reference for using AI image generators, video generators, and code-based video tools to produce ad visuals at scale.
- **Platform Specs Reference (@platform-specs-reference)**: Complete character limits, format requirements, and best practices for each ad platform.

### Address Github Comments
- **Address GitHub Comments (@address-github-comments)**: ---

### Adhx
- **ADHX - X/Twitter Post Reader (@adhx---x/twitter-post-reader)**: ---

### Advanced Evaluation
- **Advanced Evaluation (@advanced-evaluation)**: ---

### Advogado Criminal
- **ADVOGADO CRIMINALISTA SENIOR — ESPECIALISTA EM DIREITO PENAL E MARIA DA PENHA (@advogado-criminalista-senior-—-especialista-em-direito-penal-e-maria-da-penha)**: ---

### Advogado Especialista
- **ADVOGADO ESPECIALISTA ELITE — JURISTA COMPLETO (@advogado-especialista-elite-—-jurista-completo)**: ---
- **Referencias e Fontes — Advogado Especialista Elite (@referencias-e-fontes-—-advogado-especialista-elite)**: - Constituicao Federal de 1988 (com emendas ate 2025)

### Aegisops Ai
- **/aegisops-ai — Autonomous Governance Orchestrator (@/aegisops-ai-—-autonomous-governance-orchestrator)**: ---

### Agent Evaluation
- **Agent Evaluation (@agent-evaluation)**: ---

### Agent Framework Azure Ai Py
- **Agent Framework Azure Hosted Agents (@agent-framework-azure-hosted-agents)**: ---

### Agent Manager Skill
- **Agent Manager Skill (@agent-manager-skill)**: ---

### Agent Memory Mcp
- **Agent Memory Skill (@agent-memory-skill)**: ---

### Agent Memory Systems
- **Agent Memory Systems (@agent-memory-systems)**: ---

### Agent Orchestration Improve Agent
- **Agent Performance Optimization Workflow (@agent-performance-optimization-workflow)**: ---

### Agent Orchestration Multi Agent Optimize
- **Multi-Agent Optimization Toolkit (@multi-agent-optimization-toolkit)**: ---

### Agent Orchestrator
- **Agent Orchestrator (@agent-orchestrator)**: ---
- **Padroes de Orquestracao Multi-Skill (@padroes-de-orquestracao-multi-skill)**: Guia detalhado para coordenar multiplos skills em workflows complexos.
- **Taxonomia de Capacidades (Capability Tags) (@taxonomia-de-capacidades-(capability-tags))**: Categorias padrao para classificar skills no ecossistema.

### Agent Tool Builder
- **Agent Tool Builder (@agent-tool-builder)**: ---

### Agentflow
- **AgentFlow (@agentflow)**: ---

### Agentfolio
- **AgentFolio (@agentfolio)**: ---

### Agentic Actions Auditor
- **Agentic Actions Auditor (@agentic-actions-auditor)**: ---

### Agentmail
- **AgentMail — Email for AI Agents (@agentmail-—-email-for-ai-agents)**: ---

### Agentphone
- **AgentPhone (@agentphone)**: ---

### Agents Md
- **Maintaining AGENTS.md (@maintaining-agents.md)**: ---

### Ai Agent Development
- **AI Agent Development Workflow (@ai-agent-development-workflow)**: ---

### Ai Agents Architect
- **AI Agents Architect (@ai-agents-architect)**: ---

### Ai Analyzer
- **AI健康分析器 (@ai健康分析器)**: ---

### Ai Engineering Toolkit
- **AI Engineering Toolkit (@ai-engineering-toolkit)**: ---

### Ai Md
- **AI.MD v4 — The Complete AI-Native Conversion System (@ai.md-v4-—-the-complete-ai-native-conversion-system)**: ---

### Ai Ml
- **AI/ML Workflow Bundle (@ai/ml-workflow-bundle)**: ---

### Ai Native Cli
- **Agent-Friendly CLI Spec v0.1 (@agent-friendly-cli-spec-v0.1)**: ---

### Ai Product
- **AI Product Development (@ai-product-development)**: ---

### Ai Seo
- **AEO and GEO Content Patterns (@aeo-and-geo-content-patterns)**: Reusable content block patterns optimized for answer engines and AI citation.
- **AI SEO (@ai-seo)**: ---
- **How Each AI Platform Picks Sources (@how-each-ai-platform-picks-sources)**: Each AI search platform has its own search index, ranking logic, and content preferences. This guide covers what matters for getting cited on each one.

### Ai Studio Image
- **AI Studio Image — Especialista em Imagens Humanizadas (@ai-studio-image-—-especialista-em-imagens-humanizadas)**: ---
- **AI Studio Image — Guia Avancado de Prompt Engineering (@ai-studio-image-—-guia-avancado-de-prompt-engineering)**: > "Describe the scene, don't just list keywords."
- **AI Studio Image — Guia de Setup Completo (@ai-studio-image-—-guia-de-setup-completo)**: 1. Acesse https://aistudio.google.com/apikey

### Ai Wrapper Product
- **AI Wrapper Product (@ai-wrapper-product)**: ---

### Airflow Dag Patterns
- **Apache Airflow DAG Patterns (@apache-airflow-dag-patterns)**: ---
- **Apache Airflow DAG Patterns Implementation Playbook (@apache-airflow-dag-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Airtable Automation
- **Airtable Automation via Rube MCP (@airtable-automation-via-rube-mcp)**: ---

### Akf Trust Metadata
- **AKF — The AI Native File Format (@akf-—-the-ai-native-file-format)**: ---

### Algolia Search
- **Algolia Search Integration (@algolia-search-integration)**: ---

### Alpha Vantage
- **Alpha Vantage — Financial Market Data (@alpha-vantage-—-financial-market-data)**: ---

### Amazon Alexa
- **AMAZON ALEXA — Voz Inteligente com Claude (@amazon-alexa-—-voz-inteligente-com-claude)**: ---

### Amplitude Automation
- **Amplitude Automation via Rube MCP (@amplitude-automation-via-rube-mcp)**: ---

### Analytics Product
- **ANALYTICS-PRODUCT — Decida com Dados (@analytics-product-—-decida-com-dados)**: ---

### Analytics Tracking
- **Analytics Tracking & Measurement Strategy (@analytics-tracking-&-measurement-strategy)**: ---

### Analyze Project
- **/analyze-project — Root Cause Analyst Workflow (@/analyze-project-—-root-cause-analyst-workflow)**: ---
- **Sample Output: session_analysis_report.md (@sample-output:-session_analysis_report.md)**: **Generated**: 2026-03-13

### Andrej Karpathy
- **ANDREJ KARPATHY — SKILL COMPLETA v2.0 (@andrej-karpathy-—-skill-completa-v2.0)**: ---

### Android Jetpack Compose Expert
- **Android Jetpack Compose Expert (@android-jetpack-compose-expert)**: ---

### Android_Ui_Verification
- **Android UI Verification Skill (@android-ui-verification-skill)**: ---

### Angular
- **Angular Expert (@angular-expert)**: ---

### Angular Best Practices
- **Angular Best Practices (@angular-best-practices)**: ---

### Angular Migration
- **Angular Migration (@angular-migration)**: ---

### Angular State Management
- **Angular State Management (@angular-state-management)**: ---

### Angular Ui Patterns
- **Angular UI Patterns (@angular-ui-patterns)**: ---

### Animejs Animation
- **Anime.js Animation Skill (@anime.js-animation-skill)**: ---

### Anti Reversing Techniques
- **Anti-Reversing Techniques Implementation Playbook (@anti-reversing-techniques-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Antigravity Design Expert
- **Antigravity UI & Motion Design Expert (@antigravity-ui-&-motion-design-expert)**: ---

### Antigravity Skill Orchestrator
- **antigravity-skill-orchestrator (@antigravity-skill-orchestrator)**: ---

### Antigravity Workflows
- **Antigravity Workflows (@antigravity-workflows)**: ---
- **Antigravity Workflows Implementation Playbook (@antigravity-workflows-implementation-playbook)**: This document explains how an agent should execute workflow-based orchestration.

### Api Design Principles
- **API Design Checklist (@api-design-checklist)**: - [ ] Resources are nouns, not verbs
- **API Design Principles (@api-design-principles)**: ---
- **API Design Principles Implementation Playbook (@api-design-principles-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.
- **GraphQL Schema Design Patterns (@graphql-schema-design-patterns)**: ```graphql
- **REST API Best Practices (@rest-api-best-practices)**: ```

### Api Documentation
- **API Documentation Workflow (@api-documentation-workflow)**: ---

### Api Documentation Generator
- **API Documentation Generator (@api-documentation-generator)**: ---

### Api Endpoint Builder
- **API Endpoint Builder (@api-endpoint-builder)**: ---

### Api Fuzzing Bug Bounty
- **API Fuzzing for Bug Bounty (@api-fuzzing-for-bug-bounty)**: ---

### Api Patterns
- **API Documentation Principles (@api-documentation-principles)**: > Good docs = happy developers = API adoption.
- **API Patterns (@api-patterns)**: ---
- **API Security Testing (@api-security-testing)**: > Principles for testing API security. OWASP API Top 10, authentication, authorization testing.
- **API Style Selection (2025) (@api-style-selection-(2025))**: > REST vs GraphQL vs tRPC - Hangi durumda hangisi?
- **Authentication Patterns (@authentication-patterns)**: > Choose auth pattern based on use case.
- **GraphQL Principles (@graphql-principles)**: > Flexible queries for complex, interconnected data.
- **REST Principles (@rest-principles)**: > Resource-based API design - nouns not verbs.
- **Rate Limiting Principles (@rate-limiting-principles)**: > Protect your API from abuse and overload.
- **Response Format Principles (@response-format-principles)**: > Consistency is key - choose a format and stick to it.
- **Versioning Strategies (@versioning-strategies)**: > Plan for API evolution from day one.
- **tRPC Principles (@trpc-principles)**: > End-to-end type safety for TypeScript monorepos.

### Api Security Best Practices
- **API Security Best Practices (@api-security-best-practices)**: ---

### Api Security Testing
- **API Security Testing Workflow (@api-security-testing-workflow)**: ---

### Api Testing Observability Api Mock
- **API Mocking Framework (@api-mocking-framework)**: ---
- **API Mocking Implementation Playbook (@api-mocking-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Apify Actor Development
- **Actor Configuration (actor.json) (@actor-configuration-(actor.json))**: The `.actor/actor.json` file contains the Actor's configuration including metadata, schema references, and platform settings.
- **Actor Logging Reference (@actor-logging-reference)**: **ALWAYS use the `apify/log` package for logging** - This package contains critical security logic including censoring sensitive data (Apify tokens, API keys, credentials) to prevent accidental exp...
- **Actor Standby Mode Reference (@actor-standby-mode-reference)**: - **NEVER disable standby mode (`usesStandbyMode: false`) in `.actor/actor.json` without explicit permission** - Actor Standby mode solves this problem by letting you have the Actor ready in the ba...
- **Apify Actor Development (@apify-actor-development)**: ---
- **Dataset Schema Reference (@dataset-schema-reference)**: The dataset schema defines how your Actor's output data is structured, transformed, and displayed in the Output tab in the Apify Console.
- **Input Schema Reference (@input-schema-reference)**: The input schema defines the input parameters for an Actor. It's a JSON object comprising various field types supported by the Apify platform.
- **Key-Value Store Schema Reference (@key-value-store-schema-reference)**: The key-value store schema organizes keys into logical groups called collections for easier data management.
- **Output Schema Reference (@output-schema-reference)**: The Actor output schema builds upon the schemas for the dataset and key-value store. It specifies where an Actor stores its output and defines templates for accessing that output. Apify Console use...

### Apify Actorization
- **Apify Actorization (@apify-actorization)**: ---
- **CLI-Based Actorization (@cli-based-actorization)**: For languages without an SDK (Go, Rust, Java, etc.), create a wrapper script that uses the Apify CLI.
- **JavaScript/TypeScript Actorization (@javascript/typescript-actorization)**: ```bash
- **Python Actorization (@python-actorization)**: ```bash
- **Schemas and Output Configuration (@schemas-and-output-configuration)**: Map your application's inputs to `.actor/input_schema.json`. Validate against the JSON Schema from the `@apify/json_schemas` npm package (`input.schema.json`).

### Apify Audience Analysis
- **Audience Analysis (@audience-analysis)**: ---

### Apify Brand Reputation Monitoring
- **Brand Reputation Monitoring (@brand-reputation-monitoring)**: ---

### Apify Competitor Intelligence
- **Competitor Intelligence (@competitor-intelligence)**: ---

### Apify Content Analytics
- **Content Analytics (@content-analytics)**: ---

### Apify Ecommerce
- **E-commerce Data Extraction (@e-commerce-data-extraction)**: ---

### Apify Influencer Discovery
- **Influencer Discovery (@influencer-discovery)**: ---

### Apify Lead Generation
- **Lead Generation (@lead-generation)**: ---

### Apify Market Research
- **Market Research (@market-research)**: ---

### Apify Trend Analysis
- **Trend Analysis (@trend-analysis)**: ---

### Apify Ultimate Scraper
- **Universal Web Scraper (@universal-web-scraper)**: ---

### App Builder
- **Agent Coordination (@agent-coordination)**: > How App Builder orchestrates specialist agents.
- **App Builder - Application Building Orchestrator (@app-builder---application-building-orchestrator)**: ---
- **Astro Static Site Template (@astro-static-site-template)**: ---
- **CLI Tool Template (@cli-tool-template)**: ---
- **Chrome Extension Template (@chrome-extension-template)**: ---
- **Electron Desktop App Template (@electron-desktop-app-template)**: ---
- **Express.js API Template (@express.js-api-template)**: ---
- **FastAPI API Template (@fastapi-api-template)**: ---
- **Feature Building (@feature-building)**: > How to analyze and implement new features.
- **Flutter App Template (@flutter-app-template)**: ---
- **Next.js Full-Stack Template (@next.js-full-stack-template)**: ---
- **Next.js SaaS Template (@next.js-saas-template)**: ---
- **Next.js Static Site Template (@next.js-static-site-template)**: ---
- **Nuxt 3 Full-Stack Template (@nuxt-3-full-stack-template)**: ---
- **Project Scaffolding (@project-scaffolding)**: > Directory structure and core files for new projects.
- **Project Templates (@project-templates)**: ---
- **Project Type Detection (@project-type-detection)**: > Analyze user requests to determine project type and template.
- **React Native App Template (@react-native-app-template)**: ---
- **Tech Stack Selection (2025) (@tech-stack-selection-(2025))**: > Default and alternative technology choices for web applications.
- **Turborepo Monorepo Template (@turborepo-monorepo-template)**: ---

### App Store Changelog
- **App Store Changelog (@app-store-changelog)**: ---
- **App Store Release Notes Guidelines (@app-store-release-notes-guidelines)**: - Produce user-facing release notes that describe visible changes since the last tag.

### App Store Optimization
- **App Store Optimization (ASO) Skill (@app-store-optimization-(aso)-skill)**: ---
- **How to Use the App Store Optimization Skill (@how-to-use-the-app-store-optimization-skill)**: Hey Claude—I just added the "app-store-optimization" skill. Can you help me optimize my app's presence on the App Store and Google Play?

### Appdeploy
- **AppDeploy Skill (@appdeploy-skill)**: ---

### Architecture
- **Architecture Decision Framework (@architecture-decision-framework)**: ---
- **Architecture Examples (@architecture-examples)**: > Real-world architecture decisions by project type.
- **Architecture Patterns Reference (@architecture-patterns-reference)**: > Quick reference for common patterns with usage guidance.
- **Context Discovery (@context-discovery)**: > Before suggesting any architecture, gather context.
- **Pattern Selection Guidelines (@pattern-selection-guidelines)**: > Decision trees for choosing architectural patterns.
- **Trade-off Analysis & ADR (@trade-off-analysis-&-adr)**: > Document every architectural decision with trade-offs.

### Architecture Decision Records
- **Architecture Decision Records (@architecture-decision-records)**: ---

### Architecture Patterns
- **Architecture Patterns Implementation Playbook (@architecture-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Arm Cortex Expert
- **@arm-cortex-expert (@@arm-cortex-expert)**: ---

### Asana Automation
- **Asana Automation via Rube MCP (@asana-automation-via-rube-mcp)**: ---

### Ask Questions If Underspecified
- **Ask Questions If Underspecified (@ask-questions-if-underspecified)**: ---

### Astro
- **Astro Web Framework (@astro-web-framework)**: ---

### Astropy
- **Astropy (@astropy)**: ---

### Async Python Patterns
- **Async Python Patterns (@async-python-patterns)**: ---
- **Async Python Patterns Implementation Playbook (@async-python-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Attack Tree Construction
- **Attack Tree Construction (@attack-tree-construction)**: ---
- **Attack Tree Construction Implementation Playbook (@attack-tree-construction-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Audio Transcriber
- **Changelog - audio-transcriber (@changelog---audio-transcriber)**: All notable changes to the audio-transcriber skill will be documented in this file.
- **Check for Faster-Whisper (preferred - 4-5x faster) (@check-for-faster-whisper-(preferred---4-5x-faster))**: ---
- **Transcription Tools Comparison (@transcription-tools-comparison)**: Comprehensive comparison of audio transcription engines supported by the audio-transcriber skill.

### Audit Context Building
- **Deep Context Builder Skill (Ultra-Granular Pure Context Mode) (@deep-context-builder-skill-(ultra-granular-pure-context-mode))**: ---

### Audit Skills
- **Audit Skills (Premium Universal Security) (@audit-skills-(premium-universal-security))**: ---

### Auri Core
- **Auri - Core Product Skill (@auri---core-product-skill)**: ---

### Auth Implementation Patterns
- **Authentication & Authorization Implementation Patterns (@authentication-&-authorization-implementation-patterns)**: ---
- **Authentication and Authorization Implementation Patterns Implementation Playbook (@authentication-and-authorization-implementation-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Autonomous Agent Patterns
- **🕹️ Autonomous Agent Patterns (@🕹️-autonomous-agent-patterns)**: ---

### Autonomous Agents
- **Autonomous Agents (@autonomous-agents)**: ---

### Avalonia Layout Zafiro
- **Avalonia Layout with Zafiro.Avalonia (@avalonia-layout-with-zafiro.avalonia)**: ---
- **Building Generic Components (@building-generic-components)**: Reducing nesting and complexity is achieved by breaking down views into generic, reusable components.
- **Icon Usage (@icon-usage)**: `Zafiro.Avalonia` simplifies icon management using a specialized markup extension and styling options.
- **Interactions and Logic (@interactions-and-logic)**: To keep XAML clean and maintainable, minimize logic in views and avoid excessive use of converters.
- **Semantic Containers (@semantic-containers)**: Using the right container for the data type simplifies XAML and improves maintainability. `Zafiro.Avalonia` provides specialized controls for common layout patterns.
- **Theme Organization and Shared Styles (@theme-organization-and-shared-styles)**: Efficient theme organization is key to avoiding redundant XAML and ensuring visual consistency.

### Avalonia Viewmodels Zafiro
- **Avalonia ViewModels with Zafiro (@avalonia-viewmodels-with-zafiro)**: ---
- **Composition & Mapping (@composition-&-mapping)**: Ensuring your ViewModels are correctly instantiated and mapped to their corresponding Views is crucial for a maintainable application.
- **Navigation & Sections (@navigation-&-sections)**: Zafiro provides powerful abstractions for managing application-wide navigation and modular UI sections.
- **ViewModels & Commands (@viewmodels-&-commands)**: In a Zafiro-based application, ViewModels should be functional, reactive, and resilient.
- **Wizards & Flows (@wizards-&-flows)**: Complex multi-step processes are handled using the `SlimWizard` pattern. This provides a declarative way to define steps, navigation logic, and final results.

### Avalonia Zafiro Development
- **Avalonia Zafiro Development (@avalonia-zafiro-development)**: ---
- **Avalonia, Zafiro & Reactive Rules (@avalonia,-zafiro-&-reactive-rules)**: - **Strict Avalonia**: Never use `System.Drawing`; always use Avalonia types.
- **Common Patterns in Angor/Zafiro (@common-patterns-in-angor/zafiro)**: The `RefreshableCollection` pattern is used to manage lists that can be refreshed via a command, maintaining an internal `SourceCache`/`SourceList` and exposing a `ReadOnlyObservableCollection`.
- **Core Technical Skills & Architecture (@core-technical-skills-&-architecture)**: The developer must possess strong expertise in:
- **Naming & Coding Standards (@naming-&-coding-standards)**: - **Explicit Names**: Favor clarity over cleverness.
- **Zafiro Reactive Shortcuts (@zafiro-reactive-shortcuts)**: Use these Zafiro extension methods to replace standard, more verbose Reactive and DynamicData patterns.

### Avoid Ai Writing
- **Avoid AI Writing — Audit & Rewrite (@avoid-ai-writing-—-audit-&-rewrite)**: ---

### Aws Cost Cleanup
- **AWS Cost Cleanup (@aws-cost-cleanup)**: ---

### Aws Cost Optimizer
- **AWS Cost Optimizer (@aws-cost-optimizer)**: ---

### Aws Penetration Testing
- **AWS Penetration Testing (@aws-penetration-testing)**: ---
- **Advanced AWS Penetration Testing Reference (@advanced-aws-penetration-testing-reference)**: - [Training Resources](#training-resources)

### Aws Serverless
- **AWS Serverless (@aws-serverless)**: ---

### Aws Skills
- **Aws Skills (@aws-skills)**: ---

### Awt E2E Testing
- **AWT — AI-Powered E2E Testing (Beta) (@awt-—-ai-powered-e2e-testing-(beta))**: ---

### Azd Deployment
- **Azure Developer CLI (azd) Container Apps Deployment (@azure-developer-cli-(azd)-container-apps-deployment)**: ---

### Azure Ai Agents Persistent Dotnet
- **Azure.AI.Agents.Persistent (.NET) (@azure.ai.agents.persistent-(.net))**: ---

### Azure Ai Agents Persistent Java
- **Azure AI Agents Persistent SDK for Java (@azure-ai-agents-persistent-sdk-for-java)**: ---

### Azure Ai Anomalydetector Java
- **Azure AI Anomaly Detector SDK for Java (@azure-ai-anomaly-detector-sdk-for-java)**: ---

### Azure Ai Contentsafety Java
- **Azure AI Content Safety SDK for Java (@azure-ai-content-safety-sdk-for-java)**: ---

### Azure Ai Contentsafety Py
- **Azure AI Content Safety SDK for Python (@azure-ai-content-safety-sdk-for-python)**: ---

### Azure Ai Contentsafety Ts
- **Azure AI Content Safety REST SDK for TypeScript (@azure-ai-content-safety-rest-sdk-for-typescript)**: ---

### Azure Ai Contentunderstanding Py
- **Azure AI Content Understanding SDK for Python (@azure-ai-content-understanding-sdk-for-python)**: ---

### Azure Ai Document Intelligence Dotnet
- **Azure.AI.DocumentIntelligence (.NET) (@azure.ai.documentintelligence-(.net))**: ---

### Azure Ai Document Intelligence Ts
- **Azure Document Intelligence REST SDK for TypeScript (@azure-document-intelligence-rest-sdk-for-typescript)**: ---

### Azure Ai Formrecognizer Java
- **Azure Document Intelligence (Form Recognizer) SDK for Java (@azure-document-intelligence-(form-recognizer)-sdk-for-java)**: ---

### Azure Ai Ml Py
- **Azure Machine Learning SDK v2 for Python (@azure-machine-learning-sdk-v2-for-python)**: ---

### Azure Ai Openai Dotnet
- **Azure.AI.OpenAI (.NET) (@azure.ai.openai-(.net))**: ---

### Azure Ai Projects Dotnet
- **Azure.AI.Projects (.NET) (@azure.ai.projects-(.net))**: ---

### Azure Ai Projects Java
- **Azure AI Projects SDK for Java (@azure-ai-projects-sdk-for-java)**: ---

### Azure Ai Projects Py
- **Azure AI Projects Python SDK (Foundry SDK) (@azure-ai-projects-python-sdk-(foundry-sdk))**: ---

### Azure Ai Projects Ts
- **Azure AI Projects SDK for TypeScript (@azure-ai-projects-sdk-for-typescript)**: ---

### Azure Ai Textanalytics Py
- **Azure AI Text Analytics SDK for Python (@azure-ai-text-analytics-sdk-for-python)**: ---

### Azure Ai Transcription Py
- **Azure AI Transcription SDK for Python (@azure-ai-transcription-sdk-for-python)**: ---

### Azure Ai Translation Document Py
- **Azure AI Document Translation SDK for Python (@azure-ai-document-translation-sdk-for-python)**: ---

### Azure Ai Translation Text Py
- **Azure AI Text Translation SDK for Python (@azure-ai-text-translation-sdk-for-python)**: ---

### Azure Ai Translation Ts
- **Azure Translation SDKs for TypeScript (@azure-translation-sdks-for-typescript)**: ---

### Azure Ai Vision Imageanalysis Java
- **Azure AI Vision Image Analysis SDK for Java (@azure-ai-vision-image-analysis-sdk-for-java)**: ---

### Azure Ai Vision Imageanalysis Py
- **Azure AI Vision Image Analysis SDK for Python (@azure-ai-vision-image-analysis-sdk-for-python)**: ---

### Azure Ai Voicelive Dotnet
- **Azure.AI.VoiceLive (.NET) (@azure.ai.voicelive-(.net))**: ---

### Azure Ai Voicelive Java
- **Azure AI VoiceLive SDK for Java (@azure-ai-voicelive-sdk-for-java)**: ---

### Azure Ai Voicelive Py
- **Azure AI Voice Live SDK (@azure-ai-voice-live-sdk)**: ---

### Azure Ai Voicelive Ts
- **@azure/ai-voicelive (JavaScript/TypeScript) (@@azure/ai-voicelive-(javascript/typescript))**: ---

### Azure Appconfiguration Java
- **Azure App Configuration SDK for Java (@azure-app-configuration-sdk-for-java)**: ---

### Azure Appconfiguration Py
- **Azure App Configuration SDK for Python (@azure-app-configuration-sdk-for-python)**: ---

### Azure Appconfiguration Ts
- **Azure App Configuration SDK for TypeScript (@azure-app-configuration-sdk-for-typescript)**: ---

### Azure Communication Callautomation Java
- **Azure Communication Call Automation (Java) (@azure-communication-call-automation-(java))**: ---

### Azure Communication Callingserver Java
- **Azure Communication CallingServer (Java) - DEPRECATED (@azure-communication-callingserver-(java)---deprecated)**: ---

### Azure Communication Chat Java
- **Azure Communication Chat (Java) (@azure-communication-chat-(java))**: ---

### Azure Communication Common Java
- **Azure Communication Common (Java) (@azure-communication-common-(java))**: ---

### Azure Communication Sms Java
- **Azure Communication SMS (Java) (@azure-communication-sms-(java))**: ---

### Azure Compute Batch Java
- **Azure Batch SDK for Java (@azure-batch-sdk-for-java)**: ---

### Azure Containerregistry Py
- **Azure Container Registry SDK for Python (@azure-container-registry-sdk-for-python)**: ---

### Azure Cosmos Db Py
- **Cosmos DB Service Implementation (@cosmos-db-service-implementation)**: ---

### Azure Cosmos Java
- **Azure Cosmos DB SDK for Java (@azure-cosmos-db-sdk-for-java)**: ---

### Azure Cosmos Py
- **Azure Cosmos DB SDK for Python (@azure-cosmos-db-sdk-for-python)**: ---

### Azure Cosmos Rust
- **Azure Cosmos DB SDK for Rust (@azure-cosmos-db-sdk-for-rust)**: ---

### Azure Cosmos Ts
- **@azure/cosmos (TypeScript/JavaScript) (@@azure/cosmos-(typescript/javascript))**: ---

### Azure Data Tables Java
- **Azure Tables SDK for Java (@azure-tables-sdk-for-java)**: ---

### Azure Data Tables Py
- **Azure Tables SDK for Python (@azure-tables-sdk-for-python)**: ---

### Azure Eventgrid Dotnet
- **Azure.Messaging.EventGrid (.NET) (@azure.messaging.eventgrid-(.net))**: ---

### Azure Eventgrid Java
- **Azure Event Grid SDK for Java (@azure-event-grid-sdk-for-java)**: ---

### Azure Eventgrid Py
- **Azure Event Grid SDK for Python (@azure-event-grid-sdk-for-python)**: ---

### Azure Eventhub Dotnet
- **Azure.Messaging.EventHubs (.NET) (@azure.messaging.eventhubs-(.net))**: ---

### Azure Eventhub Java
- **Azure Event Hubs SDK for Java (@azure-event-hubs-sdk-for-java)**: ---

### Azure Eventhub Py
- **Azure Event Hubs SDK for Python (@azure-event-hubs-sdk-for-python)**: ---

### Azure Eventhub Rust
- **Azure Event Hubs SDK for Rust (@azure-event-hubs-sdk-for-rust)**: ---

### Azure Eventhub Ts
- **Azure Event Hubs SDK for TypeScript (@azure-event-hubs-sdk-for-typescript)**: ---

### Azure Functions
- **Azure Functions (@azure-functions)**: ---

### Azure Identity Dotnet
- **Azure.Identity (.NET) (@azure.identity-(.net))**: ---

### Azure Identity Java
- **Azure Identity (Java) (@azure-identity-(java))**: ---

### Azure Identity Py
- **Azure Identity SDK for Python (@azure-identity-sdk-for-python)**: ---

### Azure Identity Rust
- **Azure Identity SDK for Rust (@azure-identity-sdk-for-rust)**: ---

### Azure Identity Ts
- **Azure Identity SDK for TypeScript (@azure-identity-sdk-for-typescript)**: ---

### Azure Keyvault Certificates Rust
- **Azure Key Vault Certificates SDK for Rust (@azure-key-vault-certificates-sdk-for-rust)**: ---

### Azure Keyvault Keys Rust
- **Azure Key Vault Keys SDK for Rust (@azure-key-vault-keys-sdk-for-rust)**: ---

### Azure Keyvault Keys Ts
- **Azure Key Vault Keys SDK for TypeScript (@azure-key-vault-keys-sdk-for-typescript)**: ---

### Azure Keyvault Py
- **Azure Key Vault SDK for Python (@azure-key-vault-sdk-for-python)**: ---

### Azure Keyvault Secrets Rust
- **Azure Key Vault Secrets SDK for Rust (@azure-key-vault-secrets-sdk-for-rust)**: ---

### Azure Keyvault Secrets Ts
- **Azure Key Vault Secrets SDK for TypeScript (@azure-key-vault-secrets-sdk-for-typescript)**: ---

### Azure Maps Search Dotnet
- **Azure Maps (.NET) (@azure-maps-(.net))**: ---

### Azure Messaging Webpubsub Java
- **Azure Web PubSub SDK for Java (@azure-web-pubsub-sdk-for-java)**: ---

### Azure Messaging Webpubsubservice Py
- **Azure Web PubSub Service SDK for Python (@azure-web-pubsub-service-sdk-for-python)**: ---

### Azure Mgmt Apicenter Dotnet
- **Azure.ResourceManager.ApiCenter (.NET) (@azure.resourcemanager.apicenter-(.net))**: ---

### Azure Mgmt Apicenter Py
- **Azure API Center Management SDK for Python (@azure-api-center-management-sdk-for-python)**: ---

### Azure Mgmt Apimanagement Dotnet
- **Azure.ResourceManager.ApiManagement (.NET) (@azure.resourcemanager.apimanagement-(.net))**: ---

### Azure Mgmt Apimanagement Py
- **Azure API Management SDK for Python (@azure-api-management-sdk-for-python)**: ---

### Azure Mgmt Applicationinsights Dotnet
- **Azure.ResourceManager.ApplicationInsights (.NET) (@azure.resourcemanager.applicationinsights-(.net))**: ---

### Azure Mgmt Arizeaiobservabilityeval Dotnet
- **Azure.ResourceManager.ArizeAIObservabilityEval (@azure.resourcemanager.arizeaiobservabilityeval)**: ---

### Azure Mgmt Botservice Dotnet
- **Azure.ResourceManager.BotService (.NET) (@azure.resourcemanager.botservice-(.net))**: ---

### Azure Mgmt Botservice Py
- **Azure Bot Service Management SDK for Python (@azure-bot-service-management-sdk-for-python)**: ---

### Azure Mgmt Fabric Dotnet
- **Azure.ResourceManager.Fabric (.NET) (@azure.resourcemanager.fabric-(.net))**: ---

### Azure Mgmt Fabric Py
- **Azure Fabric Management SDK for Python (@azure-fabric-management-sdk-for-python)**: ---

### Azure Mgmt Mongodbatlas Dotnet
- **Azure.ResourceManager.MongoDBAtlas SDK (@azure.resourcemanager.mongodbatlas-sdk)**: ---

### Azure Mgmt Weightsandbiases Dotnet
- **Azure.ResourceManager.WeightsAndBiases (.NET) (@azure.resourcemanager.weightsandbiases-(.net))**: ---

### Azure Microsoft Playwright Testing Ts
- **Azure Playwright Workspaces SDK for TypeScript (@azure-playwright-workspaces-sdk-for-typescript)**: ---

### Azure Monitor Ingestion Java
- **Azure Monitor Ingestion SDK for Java (@azure-monitor-ingestion-sdk-for-java)**: ---

### Azure Monitor Ingestion Py
- **Azure Monitor Ingestion SDK for Python (@azure-monitor-ingestion-sdk-for-python)**: ---

### Azure Monitor Opentelemetry Exporter Java
- **Azure Monitor OpenTelemetry Exporter for Java (@azure-monitor-opentelemetry-exporter-for-java)**: ---

### Azure Monitor Opentelemetry Exporter Py
- **Azure Monitor OpenTelemetry Exporter for Python (@azure-monitor-opentelemetry-exporter-for-python)**: ---

### Azure Monitor Opentelemetry Py
- **Azure Monitor OpenTelemetry Distro for Python (@azure-monitor-opentelemetry-distro-for-python)**: ---

### Azure Monitor Opentelemetry Ts
- **Azure Monitor OpenTelemetry SDK for TypeScript (@azure-monitor-opentelemetry-sdk-for-typescript)**: ---

### Azure Monitor Query Java
- **Azure Monitor Query SDK for Java (@azure-monitor-query-sdk-for-java)**: ---

### Azure Monitor Query Py
- **Azure Monitor Query SDK for Python (@azure-monitor-query-sdk-for-python)**: ---

### Azure Postgres Ts
- **Azure PostgreSQL for TypeScript (node-postgres) (@azure-postgresql-for-typescript-(node-postgres))**: ---

### Azure Resource Manager Cosmosdb Dotnet
- **Azure.ResourceManager.CosmosDB (.NET) (@azure.resourcemanager.cosmosdb-(.net))**: ---

### Azure Resource Manager Durabletask Dotnet
- **Azure.ResourceManager.DurableTask (.NET) (@azure.resourcemanager.durabletask-(.net))**: ---

### Azure Resource Manager Mysql Dotnet
- **Azure.ResourceManager.MySql (.NET) (@azure.resourcemanager.mysql-(.net))**: ---

### Azure Resource Manager Playwright Dotnet
- **Azure.ResourceManager.Playwright (.NET) (@azure.resourcemanager.playwright-(.net))**: ---

### Azure Resource Manager Postgresql Dotnet
- **Azure.ResourceManager.PostgreSql (.NET) (@azure.resourcemanager.postgresql-(.net))**: ---

### Azure Resource Manager Redis Dotnet
- **Azure.ResourceManager.Redis (.NET) (@azure.resourcemanager.redis-(.net))**: ---

### Azure Resource Manager Sql Dotnet
- **Azure.ResourceManager.Sql (.NET) (@azure.resourcemanager.sql-(.net))**: ---

### Azure Search Documents Dotnet
- **Azure.Search.Documents (.NET) (@azure.search.documents-(.net))**: ---

### Azure Search Documents Py
- **Azure AI Search SDK for Python (@azure-ai-search-sdk-for-python)**: ---

### Azure Search Documents Ts
- **Azure AI Search SDK for TypeScript (@azure-ai-search-sdk-for-typescript)**: ---

### Azure Security Keyvault Keys Dotnet
- **Azure.Security.KeyVault.Keys (.NET) (@azure.security.keyvault.keys-(.net))**: ---

### Azure Security Keyvault Keys Java
- **Azure Key Vault Keys (Java) (@azure-key-vault-keys-(java))**: ---

### Azure Security Keyvault Secrets Java
- **Azure Key Vault Secrets (Java) (@azure-key-vault-secrets-(java))**: ---

### Azure Servicebus Dotnet
- **Azure.Messaging.ServiceBus (.NET) (@azure.messaging.servicebus-(.net))**: ---

### Azure Servicebus Py
- **Azure Service Bus SDK for Python (@azure-service-bus-sdk-for-python)**: ---

### Azure Servicebus Ts
- **Azure Service Bus SDK for TypeScript (@azure-service-bus-sdk-for-typescript)**: ---

### Azure Speech To Text Rest Py
- **Azure Speech to Text REST API for Short Audio (@azure-speech-to-text-rest-api-for-short-audio)**: ---

### Azure Storage Blob Java
- **Azure Storage Blob SDK for Java (@azure-storage-blob-sdk-for-java)**: ---

### Azure Storage Blob Py
- **Azure Blob Storage SDK for Python (@azure-blob-storage-sdk-for-python)**: ---

### Azure Storage Blob Rust
- **Azure Blob Storage SDK for Rust (@azure-blob-storage-sdk-for-rust)**: ---

### Azure Storage Blob Ts
- **@azure/storage-blob (TypeScript/JavaScript) (@@azure/storage-blob-(typescript/javascript))**: ---

### Azure Storage File Datalake Py
- **Azure Data Lake Storage Gen2 SDK for Python (@azure-data-lake-storage-gen2-sdk-for-python)**: ---

### Azure Storage File Share Py
- **Azure Storage File Share SDK for Python (@azure-storage-file-share-sdk-for-python)**: ---

### Azure Storage File Share Ts
- **@azure/storage-file-share (TypeScript/JavaScript) (@@azure/storage-file-share-(typescript/javascript))**: ---

### Azure Storage Queue Py
- **Azure Queue Storage SDK for Python (@azure-queue-storage-sdk-for-python)**: ---

### Azure Storage Queue Ts
- **@azure/storage-queue (TypeScript/JavaScript) (@@azure/storage-queue-(typescript/javascript))**: ---

### Azure Web Pubsub Ts
- **Azure Web PubSub SDKs for TypeScript (@azure-web-pubsub-sdks-for-typescript)**: ---

### Backend Dev Guidelines
- **Architecture Overview - Backend Services (@architecture-overview---backend-services)**: Complete guide to the layered architecture pattern used in backend microservices.
- **Async Patterns and Error Handling (@async-patterns-and-error-handling)**: Complete guide to async/await patterns and custom error handling.
- **Backend Development Guidelines (@backend-development-guidelines)**: ---
- **Complete Examples - Full Working Code (@complete-examples---full-working-code)**: Real-world examples showing complete implementation patterns.
- **Configuration Management - UnifiedConfig Pattern (@configuration-management---unifiedconfig-pattern)**: Complete guide to managing configuration in backend microservices.
- **Database Patterns - Prisma Best Practices (@database-patterns---prisma-best-practices)**: Complete guide to database access patterns using Prisma in backend microservices.
- **Middleware Guide - Express Middleware Patterns (@middleware-guide---express-middleware-patterns)**: Complete guide to creating and using middleware in backend microservices.
- **Routing and Controllers - Best Practices (@routing-and-controllers---best-practices)**: Complete guide to clean route definitions and controller patterns.
- **Sentry Integration and Monitoring (@sentry-integration-and-monitoring)**: Complete guide to error tracking and performance monitoring with Sentry v8.
- **Services and Repositories - Business Logic Layer (@services-and-repositories---business-logic-layer)**: Complete guide to organizing business logic with services and data access with repositories.
- **Testing Guide - Backend Testing Strategies (@testing-guide---backend-testing-strategies)**: Complete guide to testing backend services with Jest and best practices.
- **Validation Patterns - Input Validation with Zod (@validation-patterns---input-validation-with-zod)**: Complete guide to input validation using Zod schemas for type-safe validation.

### Backtesting Frameworks
- **Backtesting Frameworks (@backtesting-frameworks)**: ---
- **Backtesting Frameworks Implementation Playbook (@backtesting-frameworks-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Bamboohr Automation
- **BambooHR Automation via Rube MCP (@bamboohr-automation-via-rube-mcp)**: ---

### Basecamp Automation
- **Basecamp Automation via Rube MCP (@basecamp-automation-via-rube-mcp)**: ---

### Baseline Ui
- **Baseline UI (@baseline-ui)**: ---

### Bash Defensive Patterns
- **Bash Defensive Patterns (@bash-defensive-patterns)**: ---
- **Bash Defensive Patterns Implementation Playbook (@bash-defensive-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Bash Linux
- **Bash Linux Patterns (@bash-linux-patterns)**: ---

### Bash Scripting
- **Bash Scripting Workflow (@bash-scripting-workflow)**: ---

### Bats Testing Patterns
- **Bats Testing Patterns (@bats-testing-patterns)**: ---
- **Bats Testing Patterns Implementation Playbook (@bats-testing-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Bazel Build Optimization
- **Bazel Build Optimization (@bazel-build-optimization)**: ---

### Bdi Mental States
- **BDI Mental State Modeling (@bdi-mental-state-modeling)**: ---

### Bdistill Behavioral Xray
- **Behavioral X-Ray (@behavioral-x-ray)**: ---

### Bdistill Knowledge Extraction
- **Knowledge Extraction (@knowledge-extraction)**: ---

### Beautiful Prose
- **Beautiful Prose (Claude Skill) (@beautiful-prose-(claude-skill))**: ---

### Behavioral Modes
- **Behavioral Modes - Adaptive AI Operating Modes (@behavioral-modes---adaptive-ai-operating-modes)**: ---

### Bevy Ecs Expert
- **Bevy ECS Expert (@bevy-ecs-expert)**: ---

### Bill Gates
- **BILL GATES — AGENTE DE SIMULACAO PROFUNDA v2.0 (@bill-gates-—-agente-de-simulacao-profunda-v2.0)**: ---

### Billing Automation
- **Billing Automation (@billing-automation)**: ---
- **Billing Automation Implementation Playbook (@billing-automation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Binary Analysis Patterns
- **Binary Analysis Patterns (@binary-analysis-patterns)**: ---

### Biopython
- **Biopython: Computational Molecular Biology in Python (@biopython:-computational-molecular-biology-in-python)**: ---

### Bitbucket Automation
- **Bitbucket Automation via Rube MCP (@bitbucket-automation-via-rube-mcp)**: ---

### Blockrun
- **BlockRun (@blockrun)**: ---

### Blog Writing Guide
- **Sentry Blog Writing Skill (@sentry-blog-writing-skill)**: ---

### Blueprint
- **Blueprint — Construction Plan Generator (@blueprint-—-construction-plan-generator)**: ---

### Box Automation
- **Box Automation via Rube MCP (@box-automation-via-rube-mcp)**: ---

### Brainstorming
- **Brainstorming Ideas Into Designs (@brainstorming-ideas-into-designs)**: ---

### Brand Guidelines
- **Brand Guidelines (@brand-guidelines)**: ---

### Brand Guidelines Anthropic
- **Anthropic Brand Styling (@anthropic-brand-styling)**: ---

### Brevo Automation
- **Brevo Automation via Rube MCP (@brevo-automation-via-rube-mcp)**: ---

### Broken Authentication
- **Broken Authentication Testing (@broken-authentication-testing)**: ---

### Browser Automation
- **Browser Automation (@browser-automation)**: ---

### Browser Extension Builder
- **Browser Extension Builder (@browser-extension-builder)**: ---

### Bug Hunter
- **Bug Hunter (@bug-hunter)**: ---

### Build
- **{Feature Name} Research (@{feature-name}-research)**: ---

### Building Native Ui
- **Expo UI Guidelines (@expo-ui-guidelines)**: ---

### Bullmq Specialist
- **BullMQ Specialist (@bullmq-specialist)**: ---

### Bun Development
- **⚡ Bun Development (@⚡-bun-development)**: ---

### Burp Suite Testing
- **Burp Suite Web Application Testing (@burp-suite-web-application-testing)**: ---

### Burpsuite Project Parser
- **Burp Project Parser (@burp-project-parser)**: ---

### C4 Architecture C4 Architecture
- **C4 Architecture Documentation Workflow (@c4-architecture-documentation-workflow)**: ---

### C4 Code
- **C4 Code Level: [Directory Name] (@c4-code-level:-[directory-name])**: ---

### C4 Component
- **C4 Component Level: [Component Name] (@c4-component-level:-[component-name])**: ---

### C4 Container
- **C4 Container Level: System Deployment (@c4-container-level:-system-deployment)**: ---

### C4 Context
- **C4 Context Level: System Context (@c4-context-level:-system-context)**: ---

### Cal Com Automation
- **Cal.com Automation via Rube MCP (@cal.com-automation-via-rube-mcp)**: ---

### Calendly Automation
- **Calendly Automation via Rube MCP (@calendly-automation-via-rube-mcp)**: ---

### Canva Automation
- **Canva Automation via Rube MCP (@canva-automation-via-rube-mcp)**: ---

### Carrier Relationship Management
- **Carrier Relationship Management (@carrier-relationship-management)**: ---
- **Carrier Relationship Management — Edge Cases Reference (@carrier-relationship-management-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex carrier management situations that don't resolve through standard decision frameworks.
- **Communication Templates — Carrier Relationship Management (@communication-templates-—-carrier-relationship-management)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing carrier communications.
- **Decision Frameworks — Carrier Relationship Management (@decision-frameworks-—-carrier-relationship-management)**: This reference provides detailed decision trees, scoring matrices, negotiation models,

### Cc Skill Backend Patterns
- **Backend Development Patterns (@backend-development-patterns)**: ---

### Cc Skill Clickhouse Io
- **ClickHouse Analytics Patterns (@clickhouse-analytics-patterns)**: ---

### Cc Skill Coding Standards
- **Coding Standards & Best Practices (@coding-standards-&-best-practices)**: ---

### Cc Skill Continuous Learning
- **cc-skill-continuous-learning (@cc-skill-continuous-learning)**: ---

### Cc Skill Frontend Patterns
- **Frontend Development Patterns (@frontend-development-patterns)**: ---

### Cc Skill Project Guidelines Example
- **Project Guidelines Skill (Example) (@project-guidelines-skill-(example))**: ---

### Cc Skill Security Review
- **Security Review Skill (@security-review-skill)**: ---

### Cc Skill Strategic Compact
- **cc-skill-strategic-compact (@cc-skill-strategic-compact)**: ---

### Changelog Automation
- **Changelog Automation (@changelog-automation)**: ---
- **Changelog Automation Implementation Playbook (@changelog-automation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Chat Widget
- **Live Support Chat Widget (@live-support-chat-widget)**: ---

### Churn Prevention
- **Cancel Flow Patterns (@cancel-flow-patterns)**: Detailed cancel flow patterns by business type, billing provider, and industry.
- **Churn Prevention (@churn-prevention)**: ---
- **Dunning Playbook (@dunning-playbook)**: Complete guide to recovering failed payments and reducing involuntary churn.

### Cicd Automation Workflow Automate
- **Workflow Automation (@workflow-automation)**: ---
- **Workflow Automation Implementation Playbook (@workflow-automation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Circleci Automation
- **CircleCI Automation via Rube MCP (@circleci-automation-via-rube-mcp)**: ---

### Cirq
- **Cirq - Quantum Computing with Python (@cirq---quantum-computing-with-python)**: ---

### Citation Management
- **Citation Management (@citation-management)**: ---

### Claimable Postgres
- **Claimable Postgres (@claimable-postgres)**: ---

### Clarity Gate
- **agentskills.io compliant frontmatter (@agentskills.io-compliant-frontmatter)**: ---

### Clarvia Aeo Check
- **Clarvia AEO Check (@clarvia-aeo-check)**: ---

### Claude Ally Health
- **Claude Ally Health (@claude-ally-health)**: ---

### Claude Api
- **Agent SDK Patterns — Python (@agent-sdk-patterns-—-python)**: ```python
- **Agent SDK Patterns — TypeScript (@agent-sdk-patterns-—-typescript)**: ```typescript
- **Building LLM-Powered Applications with Claude (@building-llm-powered-applications-with-claude)**: ---
- **Claude API — C# (@claude-api-—-c#)**: > **Note:** The C# SDK is the official Anthropic SDK for C#. Tool use is supported via the Messages API. A class-annotation-based tool runner is not available; use raw tool definitions with JSON sc...
- **Claude API — Go (@claude-api-—-go)**: > **Note:** The Go SDK supports the Claude API and beta tool use with `BetaToolRunner`. Agent SDK is not yet available for Go.
- **Claude API — Java (@claude-api-—-java)**: > **Note:** The Java SDK supports the Claude API and beta tool use with annotated classes. Agent SDK is not yet available for Java.
- **Claude API — PHP (@claude-api-—-php)**: > **Note:** The PHP SDK is the official Anthropic SDK for PHP. Tool runner and Agent SDK are not available. Bedrock, Vertex AI, and Foundry clients are supported.
- **Claude API — Ruby (@claude-api-—-ruby)**: > **Note:** The Ruby SDK supports the Claude API. A tool runner is available in beta via `client.beta.messages.tool_runner()`. Agent SDK is not yet available for Ruby.
- **Claude API — cURL / Raw HTTP (@claude-api-—-curl-/-raw-http)**: Use these examples when the user needs raw HTTP requests or is working in a language without an official SDK.
- **Claude Model Catalog (@claude-model-catalog)**: **Only use exact model IDs listed in this file.** Never guess or construct model IDs — incorrect IDs will cause API errors. Use aliases wherever available. For the latest information, WebFetch the ...
- **Files API — Python (@files-api-—-python)**: The Files API uploads files for use in Messages API requests. Reference files via `file_id` in content blocks, avoiding re-uploads across multiple API calls.
- **Files API — TypeScript (@files-api-—-typescript)**: The Files API uploads files for use in Messages API requests. Reference files via `file_id` in content blocks, avoiding re-uploads across multiple API calls.
- **HTTP Error Codes Reference (@http-error-codes-reference)**: This file documents HTTP error codes returned by the Claude API, their common causes, and how to handle them. For language-specific error handling examples, see the `python/` or `typescript/` folders.
- **Live Documentation Sources (@live-documentation-sources)**: This file contains WebFetch URLs for fetching current information from platform.claude.com and Agent SDK repositories. Use these when users need the latest data that may have changed since the cach...
- **Message Batches API — Python (@message-batches-api-—-python)**: The Batches API (`POST /v1/messages/batches`) processes Messages API requests asynchronously at 50% of standard prices.
- **Message Batches API — TypeScript (@message-batches-api-—-typescript)**: The Batches API (`POST /v1/messages/batches`) processes Messages API requests asynchronously at 50% of standard prices.
- **Streaming — Python (@streaming-—-python)**: ```python
- **Streaming — TypeScript (@streaming-—-typescript)**: ```typescript
- **Tool Use Concepts (@tool-use-concepts)**: This file covers the conceptual foundations of tool use with the Claude API. For language-specific code examples, see the `python/`, `typescript/`, or other language folders.
- **Tool Use — Python (@tool-use-—-python)**: For conceptual overview (tool definitions, tool choice, tips), see [shared/tool-use-concepts.md](../../shared/tool-use-concepts.md).
- **Tool Use — TypeScript (@tool-use-—-typescript)**: For conceptual overview (tool definitions, tool choice, tips), see [shared/tool-use-concepts.md](../../shared/tool-use-concepts.md).

### Claude Code Expert
- **CLAUDE CODE EXPERT - Potencia Maxima (@claude-code-expert---potencia-maxima)**: ---

### Claude Code Guide
- **Claude Code Guide (@claude-code-guide)**: ---

### Claude D3Js Skill
- **D3.js Colour Schemes and Palette Recommendations (@d3.js-colour-schemes-and-palette-recommendations)**: Comprehensive guide to colour selection in data visualisation with d3.js.
- **D3.js Scale Reference (@d3.js-scale-reference)**: Comprehensive guide to all d3 scale types with examples and use cases.
- **D3.js Visualisation (@d3.js-visualisation)**: ---
- **D3.js Visualisation Patterns (@d3.js-visualisation-patterns)**: This reference provides detailed code patterns for common d3.js visualisation types.

### Claude In Chrome Troubleshooting
- **Claude in Chrome MCP Troubleshooting (@claude-in-chrome-mcp-troubleshooting)**: ---

### Claude Monitor
- **Claude Monitor — Diagnóstico de Performance (@claude-monitor-—-diagnóstico-de-performance)**: ---

### Claude Scientific Skills
- **Claude Scientific Skills (@claude-scientific-skills)**: ---

### Claude Settings Audit
- **Claude Settings Audit (@claude-settings-audit)**: ---

### Claude Speed Reader
- **Claude Speed Reader (@claude-speed-reader)**: ---

### Claude Win11 Speckit Update Skill
- **Claude Win11 Speckit Update Skill (@claude-win11-speckit-update-skill)**: ---

### Clean Code
- **Clean Code Skill (@clean-code-skill)**: ---

### Clerk Auth
- **Clerk Authentication (@clerk-authentication)**: ---

### Clickup Automation
- **ClickUp Automation via Rube MCP (@clickup-automation-via-rube-mcp)**: ---

### Close Automation
- **Close CRM Automation via Rube MCP (@close-crm-automation-via-rube-mcp)**: ---

### Closed Loop Delivery
- **Closed-Loop Delivery (@closed-loop-delivery)**: ---

### Cloud Devops
- **Cloud/DevOps Workflow Bundle (@cloud/devops-workflow-bundle)**: ---

### Cloud Penetration Testing
- **Advanced Cloud Pentesting Scripts (@advanced-cloud-pentesting-scripts)**: Reference: [Cloud Pentesting Cheatsheet by Beau Bullock](https://github.com/dafthack/CloudPentestCheatsheets)
- **Cloud Penetration Testing (@cloud-penetration-testing)**: ---

### Coda Automation
- **Coda Automation via Rube MCP (@coda-automation-via-rube-mcp)**: ---

### Code Documentation Code Explain
- **Code Explanation and Analysis (@code-explanation-and-analysis)**: ---
- **Code Explanation and Analysis Implementation Playbook (@code-explanation-and-analysis-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Code Refactoring Context Restore
- **Context Restoration: Advanced Semantic Memory Rehydration (@context-restoration:-advanced-semantic-memory-rehydration)**: ---

### Code Refactoring Tech Debt
- **Technical Debt Analysis and Remediation (@technical-debt-analysis-and-remediation)**: ---

### Code Review Ai Ai Review
- **AI-Powered Code Review Specialist (@ai-powered-code-review-specialist)**: ---

### Code Review Checklist
- **Code Review Checklist (@code-review-checklist)**: ---

### Code Review Excellence
- **Code Review Excellence (@code-review-excellence)**: ---
- **Code Review Excellence Implementation Playbook (@code-review-excellence-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Code Simplifier
- **Code Simplifier (@code-simplifier)**: ---

### Codebase Audit Pre Push
- **Pre-Push Codebase Audit (@pre-push-codebase-audit)**: ---

### Codebase Cleanup Refactor Clean
- **Refactor and Clean Code (@refactor-and-clean-code)**: ---
- **Refactor and Clean Code Implementation Playbook (@refactor-and-clean-code-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Codex Review
- **codex-review (@codex-review)**: ---

### Cold Email
- **Benchmarks, Data & Expert Methods (@benchmarks,-data-&-expert-methods)**: | Metric                     | Average | Good   | Excellent | Source                   |
- **Cold Email Copywriting Frameworks (@cold-email-copywriting-frameworks)**: Frameworks beat templates — they teach thinking patterns, not copy-paste shortcuts.
- **Cold Email Writing (@cold-email-writing)**: ---
- **Follow-Up Sequences (@follow-up-sequences)**: 55% of replies come from follow-ups, not the initial email. Yet 48% of salespeople never follow up even once.
- **Personalization at Scale (@personalization-at-scale)**: Personalization drives **50–250% more replies** (Lavender). The key insight: **if your personalization has nothing to do with the problem you solve, it's just an attention hack** (Clay).
- **Subject Line Optimization (@subject-line-optimization)**: The subject line determines whether the email gets read. The data is counterintuitive: **short, boring, internal-looking subject lines win decisively.**

### Comfyui Gateway
- **ComfyUI Gateway (@comfyui-gateway)**: ---
- **ComfyUI Gateway -- Integration Guide (@comfyui-gateway----integration-guide)**: Complete integration reference with ready-to-use code examples for every endpoint
- **ComfyUI Gateway -- Troubleshooting Guide (@comfyui-gateway----troubleshooting-guide)**: Comprehensive troubleshooting reference for diagnosing and resolving issues with the

### Commit
- **Sentry Commit Messages (@sentry-commit-messages)**: ---

### Competitive Landscape
- **Competitive Landscape Analysis (@competitive-landscape-analysis)**: ---
- **Competitive Landscape Analysis Implementation Playbook (@competitive-landscape-analysis-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Competitor Alternatives
- **Competitor & Alternative Pages (@competitor-&-alternative-pages)**: ---

### Computer Use Agents
- **Computer Use Agents (@computer-use-agents)**: ---

### Computer Vision Expert
- **Computer Vision Expert (SOTA 2026) (@computer-vision-expert-(sota-2026))**: ---

### Concise Planning
- **Concise Planning (@concise-planning)**: ---

### Conductor Implement
- **Implement Track (@implement-track)**: ---

### Conductor Manage
- **Track Manager (@track-manager)**: ---
- **Track Manager Implementation Playbook (@track-manager-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Conductor New Track
- **New Track (@new-track)**: ---

### Conductor Revert
- **Revert Track (@revert-track)**: ---

### Conductor Setup
- **What to Create (@what-to-create)**: ---

### Conductor Status
- **Conductor Status (@conductor-status)**: ---

### Conductor Validator
- **Check if conductor directory exists (@check-if-conductor-directory-exists)**: ---

### Confluence Automation
- **Confluence Automation via Rube MCP (@confluence-automation-via-rube-mcp)**: ---

### Constant Time Analysis
- **Constant-Time Analysis (@constant-time-analysis)**: ---

### Content Creator
- **Brand Voice & Style Guidelines (@brand-voice-&-style-guidelines)**: - **Formal**: Legal documents, investor communications, crisis responses
- **Content Calendar Template - [Month Year] (@content-calendar-template---[month-year])**: - **Traffic Goal**:
- **Content Creation Frameworks & Templates (@content-creation-frameworks-&-templates)**: ```markdown
- **Content Creator (@content-creator)**: ---
- **Social Media Optimization Guide (@social-media-optimization-guide)**: **Audience**: B2B professionals, decision-makers, thought leaders

### Content Strategy
- **Content Strategy (@content-strategy)**: ---
- **Headless CMS Guide (@headless-cms-guide)**: Reference for choosing, modeling, and implementing a headless CMS for marketing content.

### Context Agent
- **Context Agent (@context-agent)**: ---
- **Especificação de Formatos — Context Agent (@especificação-de-formatos-—-context-agent)**: Cada arquivo de sessão segue este formato:
- **Regras de Compressão e Arquivamento (@regras-de-compressão-e-arquivamento)**: Uma sessão é candidata a arquivamento quando:

### Context Compression
- **Context Compression Strategies (@context-compression-strategies)**: ---

### Context Degradation
- **Context Degradation Patterns (@context-degradation-patterns)**: ---

### Context Driven Development
- **Context-Driven Development (@context-driven-development)**: ---

### Context Fundamentals
- **Context Engineering Fundamentals (@context-engineering-fundamentals)**: ---

### Context Guardian
- **Checklist de Verificacao e Redundancia (@checklist-de-verificacao-e-redundancia)**: Em projetos tecnicos complexos, a perda de um unico detalhe pode causar horas de
- **Context Guardian (@context-guardian)**: ---
- **Protocolo de Extracao Detalhado (@protocolo-de-extracao-detalhado)**: Guia passo a passo para extrair TODAS as informacoes criticas de uma sessao

### Context Management Context Save
- **Context Save Tool: Intelligent Context Management Specialist (@context-save-tool:-intelligent-context-management-specialist)**: ---

### Context Optimization
- **Context Optimization Techniques (@context-optimization-techniques)**: ---

### Context Window Management
- **Context Window Management (@context-window-management)**: ---

### Context7 Auto Research
- **context7-auto-research (@context7-auto-research)**: ---

### Conversation Memory
- **Conversation Memory (@conversation-memory)**: ---

### Convertkit Automation
- **ConvertKit (Kit) Automation via Rube MCP (@convertkit-(kit)-automation-via-rube-mcp)**: ---

### Convex
- **Convex (@convex)**: ---

### Copilot Sdk
- **GitHub Copilot SDK (@github-copilot-sdk)**: ---

### Copy Editing
- **Copy Editing (@copy-editing)**: ---

### Copywriting
- **Copywriting (@copywriting)**: ---

### Core Components
- **Core Components (@core-components)**: ---

### Cost Optimization
- **Cloud Cost Optimization (@cloud-cost-optimization)**: ---

### Cpp Pro
- **Build Systems and Tooling (@build-systems-and-tooling)**: ```cmake
- **C++ Implementation Playbook (@c++-implementation-playbook)**: **Date:** March 23, 2026
- **Concurrency and Parallel Programming (@concurrency-and-parallel-programming)**: ```cpp
- **Memory Management & Performance (@memory-management-&-performance)**: ```cpp
- **Modern C++20/23 Features (@modern-c++20/23-features)**: ```cpp
- **Template Metaprogramming (@template-metaprogramming)**: ```cpp

### Cqrs Implementation
- **CQRS Implementation (@cqrs-implementation)**: ---
- **CQRS Implementation Playbook (@cqrs-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Create Branch
- **Create Branch (@create-branch)**: ---

### Create Issue Gate
- **Create Issue Gate (@create-issue-gate)**: ---

### Create Pr
- **Alias: create-pr (@alias:-create-pr)**: ---

### Cred Omega
- **CRED-OMEGA: Security Engine for All API Keys (Enterprise) (@cred-omega:-security-engine-for-all-api-keys-(enterprise))**: ---

### Crewai
- **CrewAI (@crewai)**: ---

### Crypto Bd Agent
- **Crypto BD Agent — Autonomous Business Development for Exchanges (@crypto-bd-agent-—-autonomous-business-development-for-exchanges)**: ---

### Customs Trade Compliance
- **Customs & Trade Compliance (@customs-&-trade-compliance)**: ---
- **Customs & Trade Compliance — Communication Templates (@customs-&-trade-compliance-—-communication-templates)**: > Tier 2 reference. Load when drafting communications with customs brokers, regulatory authorities, internal stakeholders, or trade partners.
- **Customs & Trade Compliance — Edge Cases Reference (@customs-&-trade-compliance-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous trade compliance situations that don't resolve through standard workflows.
- **Decision Frameworks — Customs & Trade Compliance (@decision-frameworks-—-customs-&-trade-compliance)**: This reference provides the detailed decision logic, classification methodology, FTA qualification

### Daily
- **Define functions using standard schema (@define-functions-using-standard-schema)**: ---

### Daily News Report
- **Daily News Report v3.0 (@daily-news-report-v3.0)**: ---

### Data Engineering Data Driven Feature
- **Data-Driven Feature Development (@data-driven-feature-development)**: ---

### Data Engineering Data Pipeline
- **Data Pipeline Architecture (@data-pipeline-architecture)**: ---

### Data Quality Frameworks
- **Data Quality Frameworks (@data-quality-frameworks)**: ---
- **Data Quality Frameworks Implementation Playbook (@data-quality-frameworks-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Data Storytelling
- **Data Storytelling (@data-storytelling)**: ---

### Data Structure Protocol
- **Data Structure Protocol (DSP) (@data-structure-protocol-(dsp))**: ---

### Database
- **Database Workflow Bundle (@database-workflow-bundle)**: ---

### Database Cloud Optimization Cost Optimize
- **Cloud Cost Optimization Implementation Playbook (@cloud-cost-optimization-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Database Design
- **Database Design (@database-design)**: ---
- **Database Selection (2025) (@database-selection-(2025))**: > Choose database based on context, not default.
- **Indexing Principles (@indexing-principles)**: > When and how to create indexes effectively.
- **Migration Principles (@migration-principles)**: > Safe migration strategy for zero-downtime changes.
- **ORM Selection (2025) (@orm-selection-(2025))**: > Choose ORM based on deployment and DX needs.
- **Query Optimization (@query-optimization)**: > N+1 problem, EXPLAIN ANALYZE, optimization priorities.
- **Schema Design Principles (@schema-design-principles)**: > Normalization, primary keys, timestamps, relationships.

### Database Migration
- **Database Migration (@database-migration)**: ---

### Database Migrations Migration Observability
- **Migration Observability and Real-time Monitoring (@migration-observability-and-real-time-monitoring)**: ---

### Database Migrations Sql Migrations
- **SQL Database Migration Strategy and Implementation (@sql-database-migration-strategy-and-implementation)**: ---
- **SQL Database Migration Strategy and Implementation Implementation Playbook (@sql-database-migration-strategy-and-implementation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Datadog Automation
- **Datadog Automation via Rube MCP (@datadog-automation-via-rube-mcp)**: ---

### Dbos Golang
- **DBOS Go Best Practices (@dbos-go-best-practices)**: ---
- **advanced-patching.md (@advanced-patching.md)**: ---
- **advanced-versioning.md (@advanced-versioning.md)**: ---
- **client-enqueue.md (@client-enqueue.md)**: ---
- **client-setup.md (@client-setup.md)**: ---
- **comm-events.md (@comm-events.md)**: ---
- **comm-messages.md (@comm-messages.md)**: ---
- **comm-streaming.md (@comm-streaming.md)**: ---
- **dbos-golang (@dbos-golang)**: > **Note:** `CLAUDE.md` is a symlink to this file.
- **lifecycle-config.md (@lifecycle-config.md)**: ---
- **pattern-debouncing.md (@pattern-debouncing.md)**: ---
- **pattern-idempotency.md (@pattern-idempotency.md)**: ---
- **pattern-scheduled.md (@pattern-scheduled.md)**: ---
- **pattern-sleep.md (@pattern-sleep.md)**: ---
- **queue-basics.md (@queue-basics.md)**: ---
- **queue-concurrency.md (@queue-concurrency.md)**: ---
- **queue-deduplication.md (@queue-deduplication.md)**: ---
- **queue-listening.md (@queue-listening.md)**: ---
- **queue-partitioning.md (@queue-partitioning.md)**: ---
- **queue-priority.md (@queue-priority.md)**: ---
- **queue-rate-limiting.md (@queue-rate-limiting.md)**: ---
- **step-basics.md (@step-basics.md)**: ---
- **step-concurrency.md (@step-concurrency.md)**: ---
- **step-retries.md (@step-retries.md)**: ---
- **test-setup.md (@test-setup.md)**: ---
- **workflow-background.md (@workflow-background.md)**: ---
- **workflow-constraints.md (@workflow-constraints.md)**: ---
- **workflow-control.md (@workflow-control.md)**: ---
- **workflow-determinism.md (@workflow-determinism.md)**: ---
- **workflow-introspection.md (@workflow-introspection.md)**: ---
- **workflow-timeout.md (@workflow-timeout.md)**: ---

### Dbos Python
- **All tasks treated equally - urgent tasks may wait (@all-tasks-treated-equally---urgent-tasks-may-wait)**: ---
- **Client code to read events (@client-code-to-read-events)**: ---
- **Client reads stream (@client-reads-stream)**: ---
- **Connection leaked - no destroy()! (@connection-leaked---no-destroy()!)**: ---
- **Create a debouncer for the workflow (@create-a-debouncer-for-the-workflow)**: ---
- **DBOS Python Best Practices (@dbos-python-best-practices)**: ---
- **Deploying new code directly kills in-progress workflows (@deploying-new-code-directly-kills-in-progress-workflows)**: ---
- **Don't configure at module level! (@don't-configure-at-module-level!)**: ---
- **Don't use external cron or manual timers (@don't-use-external-cron-or-manual-timers)**: ---
- **Don't use threads for DBOS workflows! (@don't-use-threads-for-dbos-workflows!)**: ---
- **Each process runs at most 5 tasks from this queue (@each-process-runs-at-most-5-tasks-from-this-queue)**: ---
- **Every worker processes both queues (@every-worker-processes-both-queues)**: ---
- **Instantiate BEFORE DBOS.launch() (@instantiate-before-dbos.launch())**: ---
- **Loading inputs/outputs when not needed is slow (@loading-inputs/outputs-when-not-needed-is-slow)**: ---
- **Max 50 tasks started per 30 seconds (@max-50-tasks-started-per-30-seconds)**: ---
- **Missing workflow_name and queue_name! (@missing-workflow_name-and-queue_name!)**: ---
- **Original (@original)**: ---
- **Partition queue with concurrency=1 per partition (@partition-queue-with-concurrency=1-per-partition)**: ---
- **Starting many workflows without control (@starting-many-workflows-without-control)**: ---
- **Webhook endpoint to receive payment notification (@webhook-endpoint-to-receive-payment-notification)**: ---
- **Workflow must complete within 60 seconds (@workflow-must-complete-within-60-seconds)**: ---
- **Wrong: assuming the workflow stopped immediately (@wrong:-assuming-the-workflow-stopped-immediately)**: ---
- **advanced-async.md (@advanced-async.md)**: ---
- **dbos-python (@dbos-python)**: > **Note:** `CLAUDE.md` is a symlink to this file.
- **step-transactions.md (@step-transactions.md)**: ---
- **test-fixtures.md (@test-fixtures.md)**: ---

### Dbos Typescript
- **DBOS TypeScript Best Practices (@dbos-typescript-best-practices)**: ---
- **dbos-typescript (@dbos-typescript)**: > **Note:** `CLAUDE.md` is a symlink to this file.
- **lifecycle-express.md (@lifecycle-express.md)**: ---
- **pattern-classes.md (@pattern-classes.md)**: ---

### Dbt Transformation Patterns
- **dbt Transformation Patterns (@dbt-transformation-patterns)**: ---
- **dbt Transformation Patterns Implementation Playbook (@dbt-transformation-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Ddd Context Mapping
- **Context Mapping Patterns (@context-mapping-patterns)**: - Partnership
- **DDD Context Mapping (@ddd-context-mapping)**: ---

### Ddd Strategic Design
- **DDD Strategic Design (@ddd-strategic-design)**: ---
- **Strategic Design Template (@strategic-design-template)**: | Capability | Subdomain type | Why | Owner team |

### Ddd Tactical Patterns
- **DDD Tactical Patterns (@ddd-tactical-patterns)**: ---
- **Tactical Pattern Checklist (@tactical-pattern-checklist)**: - One aggregate root per transaction boundary

### Debug Buttercup
- **Debug Buttercup (@debug-buttercup)**: ---

### Debugging Strategies
- **Debugging Strategies (@debugging-strategies)**: ---
- **Debugging Strategies Implementation Playbook (@debugging-strategies-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Deep Research
- **Gemini Deep Research Skill (@gemini-deep-research-skill)**: ---

### Defi Protocol Templates
- **DeFi Protocol Templates (@defi-protocol-templates)**: ---

### Defuddle
- **Defuddle (@defuddle)**: ---

### Dependency Management Deps Audit
- **Dependency Audit and Security Analysis (@dependency-audit-and-security-analysis)**: ---
- **Dependency Audit and Security Analysis Implementation Playbook (@dependency-audit-and-security-analysis-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Dependency Upgrade
- **Dependency Upgrade (@dependency-upgrade)**: ---

### Deployment Pipeline Design
- **Deployment Pipeline Design (@deployment-pipeline-design)**: ---

### Deployment Procedures
- **Deployment Procedures (@deployment-procedures)**: ---

### Deployment Validation Config Validate
- **Configuration Validation (@configuration-validation)**: ---

### Design Md
- **Stitch DESIGN.md Skill (@stitch-design.md-skill)**: ---

### Design Orchestration
- **Design Orchestration (Meta-Skill) (@design-orchestration-(meta-skill))**: ---

### Design Spells
- **Design Spells Skill (@design-spells-skill)**: ---

### Devcontainer Setup
- **Devcontainer Setup Skill (@devcontainer-setup-skill)**: ---

### Development
- **Development Workflow Bundle (@development-workflow-bundle)**: ---

### Devops Deploy
- **DEVOPS-DEPLOY — Da Ideia para Producao (@devops-deploy-—-da-ideia-para-producao)**: ---

### Diary
- **專案實作紀錄：{專案名稱} (@專案實作紀錄：{專案名稱})**: * **📅 日期**：YYYY-MM-DD
- **📔 Unified Diary System (@📔-unified-diary-system)**: ---
- **📔 YYYY-MM-DD 全域進度總覽 (@📔-yyyy-mm-dd-全域進度總覽)**: > 🌟 **今日亮點 (Daily Highlight)**

### Differential Review
- **Differential Security Review (@differential-security-review)**: ---

### Discord Automation
- **Discord Automation via Rube MCP (@discord-automation-via-rube-mcp)**: ---

### Discord Bot Architect
- **Discord Bot Architect (@discord-bot-architect)**: ---

### Dispatching Parallel Agents
- **Dispatching Parallel Agents (@dispatching-parallel-agents)**: ---

### Distributed Debugging Debug Trace
- **Debug and Trace Configuration (@debug-and-trace-configuration)**: ---
- **Debug and Trace Configuration Implementation Playbook (@debug-and-trace-configuration-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Distributed Tracing
- **Distributed Tracing (@distributed-tracing)**: ---

### Django Access Review
- **Django Access Control & IDOR Review (@django-access-control-&-idor-review)**: ---

### Django Perf Review
- **Django Performance Review (@django-performance-review)**: ---

### Doc Coauthoring
- **Doc Co-Authoring Workflow (@doc-co-authoring-workflow)**: ---

### Docker Expert
- **Docker Expert (@docker-expert)**: ---

### Documentation
- **Documentation Workflow Bundle (@documentation-workflow-bundle)**: ---

### Documentation Generation Doc Generate
- **Automated Documentation Generation (@automated-documentation-generation)**: ---
- **Automated Documentation Generation Implementation Playbook (@automated-documentation-generation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Documentation Templates
- **Documentation Templates (@documentation-templates)**: ---

### Docusign Automation
- **DocuSign Automation via Rube MCP (@docusign-automation-via-rube-mcp)**: ---

### Docx Official
- **DOCX Library Tutorial (@docx-library-tutorial)**: Generate .docx files with JavaScript/TypeScript.
- **DOCX creation, editing, and analysis (@docx-creation,-editing,-and-analysis)**: ---
- **Office Open XML Technical Reference (@office-open-xml-technical-reference)**: **Important: Read this entire document before starting.** This document covers:

### Domain Driven Design
- **DDD Deliverables Checklist (@ddd-deliverables-checklist)**: Use this checklist to keep DDD adoption practical and measurable.
- **Domain-Driven Design (@domain-driven-design)**: ---

### Dotnet Backend
- **.NET Backend Agent - ASP.NET Core & Enterprise API Expert (@.net-backend-agent---asp.net-core-&-enterprise-api-expert)**: ---

### Dotnet Backend Patterns
- **.NET Backend Development Patterns (@.net-backend-development-patterns)**: ---
- **.NET Backend Development Patterns Implementation Playbook (@.net-backend-development-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.
- **Dapper Patterns and Best Practices (@dapper-patterns-and-best-practices)**: Advanced patterns for high-performance data access with Dapper in .NET.
- **Entity Framework Core Best Practices (@entity-framework-core-best-practices)**: Performance optimization and best practices for EF Core in production applications.

### Drizzle Orm Expert
- **Drizzle ORM Expert (@drizzle-orm-expert)**: ---

### Dropbox Automation
- **Dropbox Automation via Rube MCP (@dropbox-automation-via-rube-mcp)**: ---

### E2E Testing
- **E2E Testing Workflow (@e2e-testing-workflow)**: ---

### E2E Testing Patterns
- **E2E Testing Patterns (@e2e-testing-patterns)**: ---
- **E2E Testing Patterns Implementation Playbook (@e2e-testing-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Earllm Build
- **EarLLM One — Build & Maintain (@earllm-one-—-build-&-maintain)**: ---

### Electron Development
- **Electron Development (@electron-development)**: ---

### Elon Musk
- **ELON MUSK — AGENTE DE SIMULACAO PROFUNDA v3.0 (@elon-musk-—-agente-de-simulacao-profunda-v3.0)**: ---
- **Elon Musk — Referência Técnica Ultra-Detalhada (@elon-musk-—-referência-técnica-ultra-detalhada)**: > Arquivo de referência para o agente elon-musk. Contém dados técnicos reais e específicos

### Email Sequence
- **Email Sequence Design (@email-sequence-design)**: ---

### Email Systems
- **Email Systems (@email-systems)**: ---

### Embedding Strategies
- **Embedding Strategies (@embedding-strategies)**: ---

### Emblemai Crypto Wallet
- **EmblemAI Crypto Wallet (@emblemai-crypto-wallet)**: ---

### Emergency Card
- **紧急医疗信息卡生成器 (@紧急医疗信息卡生成器)**: ---

### Employment Contract Templates
- **Employment Contract Templates (@employment-contract-templates)**: ---
- **Employment Contract Templates Implementation Playbook (@employment-contract-templates-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Energy Procurement
- **Communication Templates — Energy Procurement (@communication-templates-—-energy-procurement)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing energy procurement communications.
- **Decision Frameworks — Energy Procurement (@decision-frameworks-—-energy-procurement)**: This reference provides detailed decision trees, evaluation matrices, financial models,
- **Energy Procurement (@energy-procurement)**: ---
- **Energy Procurement — Edge Cases Reference (@energy-procurement-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex energy procurement situations that don't resolve through standard decision frameworks.

### Enhance Prompt
- **Enhance Prompt for Stitch (@enhance-prompt-for-stitch)**: ---

### Environment Setup Guide
- **Environment Setup Guide (@environment-setup-guide)**: ---

### Error Diagnostics Error Analysis
- **Error Analysis and Resolution (@error-analysis-and-resolution)**: ---
- **Error Analysis and Resolution Implementation Playbook (@error-analysis-and-resolution-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Error Diagnostics Error Trace
- **Error Tracking and Monitoring (@error-tracking-and-monitoring)**: ---
- **Error Tracking and Monitoring Implementation Playbook (@error-tracking-and-monitoring-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Error Handling Patterns
- **Error Handling Patterns (@error-handling-patterns)**: ---
- **Error Handling Patterns Implementation Playbook (@error-handling-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Ethical Hacking Methodology
- **Ethical Hacking Methodology (@ethical-hacking-methodology)**: ---

### Evaluation
- **Evaluation Methods for Agent Systems (@evaluation-methods-for-agent-systems)**: ---

### Event Sourcing Architect
- **Event Sourcing Architect (@event-sourcing-architect)**: ---

### Event Store Design
- **Event Store Design (@event-store-design)**: ---
- **Event Store Design Playbook (@event-store-design-playbook)**: - Use append-only writes with optimistic concurrency.

### Evolution
- **Makepad Skills Evolution (@makepad-skills-evolution)**: ---

### Exa Search
- **exa-search (@exa-search)**: ---

### Executing Plans
- **Executing Plans (@executing-plans)**: ---

### Explain Like Socrates
- **EXPLAIN LIKE SOCRATES (@explain-like-socrates)**: ---

### Expo Api Routes
- **Create a secret (@create-a-secret)**: ---

### Expo Cicd Workflows
- **EAS Workflows Skill (@eas-workflows-skill)**: ---

### Expo Deployment
- **Expo Deployment (@expo-deployment)**: ---

### Expo Dev Client
- **iOS (requires Xcode) (@ios-(requires-xcode))**: ---

### Expo Tailwind Setup
- **Tailwind CSS Setup for Expo with react-native-css (@tailwind-css-setup-for-expo-with-react-native-css)**: ---

### Faf Expert
- **FAF Expert - Advanced AI Context Architecture (@faf-expert---advanced-ai-context-architecture)**: ---

### Faf Wizard
- **FAF Wizard - One-Click AI Intelligence (@faf-wizard---one-click-ai-intelligence)**: ---

### Fal Audio
- **Fal Audio (@fal-audio)**: ---

### Fal Generate
- **Fal Generate (@fal-generate)**: ---

### Fal Image Edit
- **Fal Image Edit (@fal-image-edit)**: ---

### Fal Platform
- **Fal Platform (@fal-platform)**: ---

### Fal Upscale
- **Fal Upscale (@fal-upscale)**: ---

### Fal Workflow
- **Fal Workflow (@fal-workflow)**: ---

### Family Health Analyzer
- **家庭健康分析技能 (@家庭健康分析技能)**: ---

### Fastapi Router Py
- **FastAPI Router (@fastapi-router)**: ---

### Fastapi Templates
- **FastAPI Project Templates (@fastapi-project-templates)**: ---
- **FastAPI Project Templates Implementation Playbook (@fastapi-project-templates-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Fda Food Safety Auditor
- **FDA Food Safety Auditor (@fda-food-safety-auditor)**: ---

### Fda Medtech Compliance Auditor
- **FDA MedTech Compliance Auditor (@fda-medtech-compliance-auditor)**: ---

### Ffuf Claude Skill
- **Ffuf Claude Skill (@ffuf-claude-skill)**: ---

### Ffuf Web Fuzzing
- **FFUF (Fuzz Faster U Fool) Skill (@ffuf-(fuzz-faster-u-fool)-skill)**: ---

### Figma Automation
- **Figma Automation via Rube MCP (@figma-automation-via-rube-mcp)**: ---

### File Organizer
- **File Organizer (@file-organizer)**: ---

### File Path Traversal
- **File Path Traversal Testing (@file-path-traversal-testing)**: ---

### File Uploads
- **File Uploads & Storage (@file-uploads-&-storage)**: ---

### Filesystem Context
- **Filesystem-Based Context Engineering (@filesystem-based-context-engineering)**: ---

### Find Bugs
- **Find Bugs (@find-bugs)**: ---

### Finishing A Development Branch
- **Finishing a Development Branch (@finishing-a-development-branch)**: ---

### Firebase
- **Firebase (@firebase)**: ---

### Firecrawl Scraper
- **firecrawl-scraper (@firecrawl-scraper)**: ---

### Firmware Analyst
- **Download from vendor (@download-from-vendor)**: ---

### Fitness Analyzer
- **运动分析器技能 (@运动分析器技能)**: ---

### Fix Review
- **Fix Review (@fix-review)**: ---

### Fixing Accessibility
- **fixing-accessibility (@fixing-accessibility)**: ---

### Fixing Motion Performance
- **fixing-motion-performance (@fixing-motion-performance)**: ---

### Flutter Expert
- **SKILL.md (@skill.md)**: ---

### Food Database Query
- **食物数据库查询技能 (@食物数据库查询技能)**: ---

### Form Cro
- **Form Conversion Rate Optimization (Form CRO) (@form-conversion-rate-optimization-(form-cro))**: ---

### Fp Async
- **Practical Async Patterns with fp-ts (@practical-async-patterns-with-fp-ts)**: ---

### Fp Backend
- **fp-ts Backend Patterns (@fp-ts-backend-patterns)**: ---

### Fp Data Transforms
- **Practical Data Transformations (@practical-data-transformations)**: ---

### Fp Either Ref
- **Either Quick Reference (@either-quick-reference)**: ---

### Fp Errors
- **Practical Error Handling with fp-ts (@practical-error-handling-with-fp-ts)**: ---

### Fp Option Ref
- **Option Quick Reference (@option-quick-reference)**: ---

### Fp Pipe Ref
- **pipe & flow Quick Reference (@pipe-&-flow-quick-reference)**: ---

### Fp Refactor
- **Refactoring Imperative Code to fp-ts (@refactoring-imperative-code-to-fp-ts)**: ---

### Fp Taskeither Ref
- **TaskEither Quick Reference (@taskeither-quick-reference)**: ---

### Fp Ts Pragmatic
- **Pragmatic Functional Programming (@pragmatic-functional-programming)**: ---

### Fp Ts React
- **Functional Programming in React (@functional-programming-in-react)**: ---

### Fp Types Ref
- **fp-ts Quick Reference (@fp-ts-quick-reference)**: ---

### Framework Migration Code Migrate
- **Code Migration Assistant (@code-migration-assistant)**: ---
- **Code Migration Assistant Implementation Playbook (@code-migration-assistant-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Framework Migration Deps Upgrade
- **Dependency Upgrade Strategy (@dependency-upgrade-strategy)**: ---
- **Dependency Upgrade Strategy Implementation Playbook (@dependency-upgrade-strategy-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Framework Migration Legacy Modernize
- **Legacy Code Modernization Workflow (@legacy-code-modernization-workflow)**: ---

### Free Tool Strategy
- **Free Tool Strategy (Engineering as Marketing) (@free-tool-strategy-(engineering-as-marketing))**: ---

### Freshdesk Automation
- **Freshdesk Automation via Rube MCP (@freshdesk-automation-via-rube-mcp)**: ---

### Freshservice Automation
- **Freshservice Automation via Rube MCP (@freshservice-automation-via-rube-mcp)**: ---

### Frontend Design
- **Frontend Design (Distinctive, Production-Grade) (@frontend-design-(distinctive,-production-grade))**: ---

### Frontend Dev Guidelines
- **Common Patterns (@common-patterns)**: Frequently used patterns for forms, authentication, DataGrid, dialogs, and other common UI elements.
- **Complete Examples (@complete-examples)**: Full working examples combining all modern patterns: React.FC, lazy loading, Suspense, useSuspenseQuery, styling, routing, and error handling.
- **Component Patterns (@component-patterns)**: Modern React component architecture for the application emphasizing type safety, lazy loading, and Suspense boundaries.
- **Data Fetching Patterns (@data-fetching-patterns)**: Modern data fetching using TanStack Query with Suspense boundaries, cache-first strategies, and centralized API services.
- **File Organization (@file-organization)**: Proper file and directory structure for maintainable, scalable frontend code in the the application.
- **Frontend Development Guidelines (@frontend-development-guidelines)**: ---
- **Loading & Error States (@loading-&-error-states)**: **CRITICAL**: Proper loading and error state handling prevents layout shift and provides better user experience.
- **Performance Optimization (@performance-optimization)**: Patterns for optimizing React component performance, preventing unnecessary re-renders, and avoiding memory leaks.
- **Routing Guide (@routing-guide)**: TanStack Router implementation with folder-based routing and lazy loading patterns.
- **Styling Guide (@styling-guide)**: Modern styling patterns for using MUI v7 sx prop, inline styles, and theme integration.
- **TypeScript Standards (@typescript-standards)**: TypeScript best practices for type safety and maintainability in React frontend code.

### Frontend Mobile Development Component Scaffold
- **React/React Native Component Scaffolding (@react/react-native-component-scaffolding)**: ---

### Frontend Mobile Security Xss Scan
- **XSS Vulnerability Scanner for Frontend Code (@xss-vulnerability-scanner-for-frontend-code)**: ---

### Frontend Slides
- **Animation Patterns Reference (@animation-patterns-reference)**: Use this reference when generating presentations. Match animations to the intended feeling.
- **Frontend Slides (@frontend-slides)**: ---
- **HTML Presentation Template (@html-presentation-template)**: Reference architecture for generating slide presentations. Every presentation follows this structure.
- **Style Presets Reference (@style-presets-reference)**: Curated visual styles for Frontend Slides. Each preset is inspired by real design references — no generic "AI slop" aesthetics. **Abstract shapes only — no illustrations.**

### Frontend Ui Dark Ts
- **Frontend UI Dark Theme (TypeScript) (@frontend-ui-dark-theme-(typescript))**: ---

### Game Development
- **2D Game Development (@2d-game-development)**: ---
- **3D Game Development (@3d-game-development)**: ---
- **Game Art Principles (@game-art-principles)**: ---
- **Game Audio Principles (@game-audio-principles)**: ---
- **Game Design Principles (@game-design-principles)**: ---
- **Game Development (@game-development)**: ---
- **Mobile Game Development (@mobile-game-development)**: ---
- **Multiplayer Game Development (@multiplayer-game-development)**: ---
- **PC/Console Game Development (@pc/console-game-development)**: ---
- **VR/AR Development (@vr/ar-development)**: ---
- **Web Browser Game Development (@web-browser-game-development)**: ---

### Gcp Cloud Run
- **GCP Cloud Run (@gcp-cloud-run)**: ---

### Gdb Cli
- **GDB Debugging Assistant (@gdb-debugging-assistant)**: ---

### Gdpr Data Handling
- **GDPR Data Handling (@gdpr-data-handling)**: ---
- **GDPR Data Handling Implementation Playbook (@gdpr-data-handling-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Gemini Api Dev
- **Gemini API Development Skill (@gemini-api-development-skill)**: ---

### Gemini Api Integration
- **Gemini API Integration (@gemini-api-integration)**: ---

### General
- **SaaS Architect (@saas-architect)**: This playbook provides expert guidance on building modern SaaS applications.
- **Workflow Bundles (@workflow-bundles)**: Consolidated and granular workflow bundles that orchestrate multiple skills for specific development and operational scenarios.

### Geo Fundamentals
- **GEO Fundamentals (@geo-fundamentals)**: ---

### Geoffrey Hinton
- **SKILL: Geoffrey Hinton — Agente Persona v2.0 (@skill:-geoffrey-hinton-—-agente-persona-v2.0)**: ---

### Gh Review Requests
- **GitHub Review Requests (@github-review-requests)**: ---

### Gha Security Review
- **GitHub Actions Security Review (@github-actions-security-review)**: ---

### Git Advanced Workflows
- **Git Advanced Workflows (@git-advanced-workflows)**: ---

### Git Hooks Automation
- **Git Hooks Automation (@git-hooks-automation)**: ---

### Git Pr Workflows Git Workflow
- **Complete Git Workflow with Multi-Agent Orchestration (@complete-git-workflow-with-multi-agent-orchestration)**: ---

### Git Pr Workflows Onboard
- **Onboard (@onboard)**: ---

### Git Pr Workflows Pr Enhance
- **Pull Request Enhancement (@pull-request-enhancement)**: ---
- **Pull Request Enhancement Implementation Playbook (@pull-request-enhancement-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Git Pushing
- **Git Push Workflow (@git-push-workflow)**: ---

### Github
- **GitHub Skill (@github-skill)**: ---

### Github Actions Templates
- **GitHub Actions Templates (@github-actions-templates)**: ---

### Github Automation
- **GitHub Automation via Rube MCP (@github-automation-via-rube-mcp)**: ---

### Github Issue Creator
- **GitHub Issue Creator (@github-issue-creator)**: ---

### Github Workflow Automation
- **🔧 GitHub Workflow Automation (@🔧-github-workflow-automation)**: ---

### Gitlab Automation
- **GitLab Automation via Rube MCP (@gitlab-automation-via-rube-mcp)**: ---

### Gitlab Ci Patterns
- **GitLab CI Patterns (@gitlab-ci-patterns)**: ---

### Gitops Workflow
- **ArgoCD Setup and Configuration (@argocd-setup-and-configuration)**: ```bash
- **GitOps Sync Policies (@gitops-sync-policies)**: ```yaml
- **GitOps Workflow (@gitops-workflow)**: ---

### Global Chat Agent Discovery
- **Global Chat Agent Discovery (@global-chat-agent-discovery)**: ---

### Gmail Automation
- **Gmail (@gmail)**: ---

### Go Concurrency Patterns
- **Go Concurrency Patterns (@go-concurrency-patterns)**: ---
- **Go Concurrency Patterns Implementation Playbook (@go-concurrency-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Go Playwright
- **Playwright Go Automation - Implementation Playbook (@playwright-go-automation---implementation-playbook)**: ```go
- **Playwright Go Automation Expert (@playwright-go-automation-expert)**: ---

### Go Rod Master
- **Go-Rod API Quick Reference (@go-rod-api-quick-reference)**: Cheat sheet for the most-used `go-rod/rod` and `go-rod/stealth` APIs.
- **Go-Rod Browser Automation Master (@go-rod-browser-automation-master)**: ---

### Goal Analyzer
- **健康目标分析器技能 (@健康目标分析器技能)**: ---

### Godot 4 Migration
- **Godot 4 Migration Guide (@godot-4-migration-guide)**: ---

### Godot Gdscript Patterns
- **Godot GDScript Patterns (@godot-gdscript-patterns)**: ---
- **Godot GDScript Patterns Implementation Playbook (@godot-gdscript-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Google Analytics Automation
- **Google Analytics Automation via Rube MCP (@google-analytics-automation-via-rube-mcp)**: ---

### Google Calendar Automation
- **Google Calendar (@google-calendar)**: ---

### Google Docs Automation
- **Google Docs (@google-docs)**: ---

### Google Drive Automation
- **Google Drive (@google-drive)**: ---

### Google Sheets Automation
- **Google Sheets (@google-sheets)**: ---

### Google Slides Automation
- **Google Slides (@google-slides)**: ---

### Googlesheets Automation
- **Google Sheets Automation via Rube MCP (@google-sheets-automation-via-rube-mcp)**: ---

### Grafana Dashboards
- **Grafana Dashboards (@grafana-dashboards)**: ---

### Graphql
- **GraphQL (@graphql)**: ---

### Growth Engine
- **GROWTH-ENGINE -- Crescimento Exponencial (@growth-engine----crescimento-exponencial)**: ---

### Grpc Golang
- **gRPC Golang (gRPC-Go) (@grpc-golang-(grpc-go))**: ---
- **gRPC Golang Implementation Playbook (@grpc-golang-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Health Trend Analyzer
- **健康趋势分析器 (@健康趋势分析器)**: ---

### Helm Chart Scaffolding
- **Helm Chart Scaffolding (@helm-chart-scaffolding)**: ---
- **Helm Chart Scaffolding Implementation Playbook (@helm-chart-scaffolding-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.
- **Helm Chart Structure Reference (@helm-chart-structure-reference)**: Complete guide to Helm chart organization, file conventions, and best practices.

### Helpdesk Automation
- **HelpDesk Automation via Rube MCP (@helpdesk-automation-via-rube-mcp)**: ---

### Hierarchical Agent Memory
- **Hierarchical Agent Memory (HAM) (@hierarchical-agent-memory-(ham))**: ---

### Hig Components Content
- **Activity views (@activity-views)**: ---
- **Apple HIG: Content Components (@apple-hig:-content-components)**: ---
- **Charts (@charts)**: ---
- **Collections (@collections)**: ---
- **Color wells (@color-wells)**: ---
- **Image views (@image-views)**: ---
- **Image wells (@image-wells)**: ---
- **Lockups (@lockups)**: ---
- **Web views (@web-views)**: ---

### Hig Components Controls
- **Apple HIG: Selection and Input Controls (@apple-hig:-selection-and-input-controls)**: ---
- **Combo boxes (@combo-boxes)**: ---
- **Controls (@controls)**: ---
- **Gauges (@gauges)**: ---
- **Labels (@labels)**: ---
- **Pickers (@pickers)**: ---
- **Rating indicators (@rating-indicators)**: ---
- **Segmented controls (@segmented-controls)**: ---
- **Sliders (@sliders)**: ---
- **Steppers (@steppers)**: ---
- **Text fields (@text-fields)**: ---
- **Text views (@text-views)**: ---
- **Toggles (@toggles)**: ---
- **Token fields (@token-fields)**: ---
- **Virtual keyboards (@virtual-keyboards)**: ---

### Hig Components Dialogs
- **Action sheets (@action-sheets)**: ---
- **Alerts (@alerts)**: ---
- **Apple HIG: Presentation Components (@apple-hig:-presentation-components)**: ---
- **Digit entry views (@digit-entry-views)**: ---
- **Popovers (@popovers)**: ---

### Hig Components Layout
- **Apple HIG: Layout and Navigation Components (@apple-hig:-layout-and-navigation-components)**: ---
- **Boxes (@boxes)**: ---
- **Column views (@column-views)**: ---
- **Lists and tables (@lists-and-tables)**: ---
- **Ornaments (@ornaments)**: ---
- **Outline views (@outline-views)**: ---
- **Panels (@panels)**: ---
- **Scroll views (@scroll-views)**: ---
- **Sidebars (@sidebars)**: ---
- **Split views (@split-views)**: ---
- **Tab bars (@tab-bars)**: ---
- **Tab views (@tab-views)**: ---
- **Windows (@windows)**: ---

### Hig Components Menus
- **Action button (@action-button)**: ---
- **Apple HIG: Menus and Buttons (@apple-hig:-menus-and-buttons)**: ---
- **Buttons (@buttons)**: ---
- **Context menus (@context-menus)**: ---
- **Disclosure controls (@disclosure-controls)**: ---
- **Dock menus (@dock-menus)**: ---
- **Edit menus (@edit-menus)**: ---
- **Menus (@menus)**: ---
- **Pop-up buttons (@pop-up-buttons)**: ---
- **Pull-down buttons (@pull-down-buttons)**: ---
- **The menu bar (@the-menu-bar)**: ---
- **Toolbars (@toolbars)**: ---

### Hig Components Search
- **Apple HIG: Navigation Components (@apple-hig:-navigation-components)**: ---
- **Page controls (@page-controls)**: ---
- **Path controls (@path-controls)**: ---
- **Search fields (@search-fields)**: ---

### Hig Components Status
- **Activity rings (@activity-rings)**: ---
- **Apple HIG: Status Components (@apple-hig:-status-components)**: ---
- **Progress indicators (@progress-indicators)**: ---
- **Status bars (@status-bars)**: ---

### Hig Components System
- **App Clips (@app-clips)**: ---
- **App Shortcuts (@app-shortcuts)**: ---
- **Apple HIG: System Experiences (@apple-hig:-system-experiences)**: ---
- **Complications (@complications)**: ---
- **Home Screen quick actions (@home-screen-quick-actions)**: ---
- **Live Activities (@live-activities)**: ---
- **Notifications (@notifications)**: ---
- **Top Shelf (@top-shelf)**: ---
- **Watch faces (@watch-faces)**: ---
- **Widgets (@widgets)**: ---

### Hig Foundations
- **Accessibility (@accessibility)**: ---
- **App icons (@app-icons)**: ---
- **Apple HIG: Design Foundations (@apple-hig:-design-foundations)**: ---
- **Branding (@branding)**: ---
- **Color (@color)**: ---
- **Dark Mode (@dark-mode)**: ---
- **Icons (@icons)**: ---
- **Images (@images)**: ---
- **Immersive experiences (@immersive-experiences)**: ---
- **Inclusion (@inclusion)**: ---
- **Layout (@layout)**: ---
- **Materials (@materials)**: ---
- **Motion (@motion)**: ---
- **Privacy (@privacy)**: ---
- **Right to left (@right-to-left)**: ---
- **SF Symbols (@sf-symbols)**: ---
- **Spatial layout (@spatial-layout)**: ---
- **Typography (@typography)**: ---
- **Writing (@writing)**: ---

### Hig Inputs
- **Apple HIG: Inputs (@apple-hig:-inputs)**: ---
- **Apple Pencil and Scribble (@apple-pencil-and-scribble)**: ---
- **Camera Control (@camera-control)**: ---
- **Digital Crown (@digital-crown)**: ---
- **Eyes (@eyes)**: ---
- **Focus and selection (@focus-and-selection)**: ---
- **Game controls (@game-controls)**: ---
- **Gestures (@gestures)**: ---
- **Gyroscope and accelerometer (@gyroscope-and-accelerometer)**: ---
- **Keyboards (@keyboards)**: ---
- **Nearby interactions (@nearby-interactions)**: ---
- **Pointing devices (@pointing-devices)**: ---
- **Remotes (@remotes)**: ---

### Hig Patterns
- **Apple HIG: Interaction Patterns (@apple-hig:-interaction-patterns)**: ---
- **Charting data (@charting-data)**: ---
- **Collaboration and sharing (@collaboration-and-sharing)**: ---
- **Drag and drop (@drag-and-drop)**: ---
- **Entering data (@entering-data)**: ---
- **Feedback (@feedback)**: ---
- **File management (@file-management)**: ---
- **Going full screen (@going-full-screen)**: ---
- **Launching (@launching)**: ---
- **Live-viewing apps (@live-viewing-apps)**: ---
- **Loading (@loading)**: ---
- **Managing accounts (@managing-accounts)**: ---
- **Managing notifications (@managing-notifications)**: ---
- **Modality (@modality)**: ---
- **Multitasking (@multitasking)**: ---
- **Offering help (@offering-help)**: ---
- **Onboarding (@onboarding)**: ---
- **Playing audio (@playing-audio)**: ---
- **Playing haptics (@playing-haptics)**: ---
- **Playing video (@playing-video)**: ---
- **Printing (@printing)**: ---
- **Ratings and reviews (@ratings-and-reviews)**: ---
- **Searching (@searching)**: ---
- **Settings (@settings)**: ---
- **Undo and redo (@undo-and-redo)**: ---
- **Workouts (@workouts)**: ---

### Hig Platforms
- **Apple HIG: Platform Design (@apple-hig:-platform-design)**: ---
- **Designing for games (@designing-for-games)**: ---
- **Designing for iOS (@designing-for-ios)**: ---
- **Designing for iPadOS (@designing-for-ipados)**: ---
- **Designing for macOS (@designing-for-macos)**: ---
- **Designing for tvOS (@designing-for-tvos)**: ---
- **Designing for visionOS (@designing-for-visionos)**: ---
- **Designing for watchOS (@designing-for-watchos)**: ---

### Hig Project Context
- **Apple HIG: Project Context (@apple-hig:-project-context)**: ---

### Hig Technologies
- **AirPlay (@airplay)**: ---
- **Always On (@always-on)**: ---
- **Apple HIG: Technologies (@apple-hig:-technologies)**: ---
- **Apple Pay (@apple-pay)**: ---
- **Augmented reality (@augmented-reality)**: ---
- **CarPlay (@carplay)**: ---
- **CareKit (@carekit)**: ---
- **Game Center (@game-center)**: ---
- **Generative AI (@generative-ai)**: ---
- **HealthKit (@healthkit)**: ---
- **HomeKit (@homekit)**: ---
- **ID Verifier (@id-verifier)**: ---
- **In-app purchase (@in-app-purchase)**: ---
- **Live Photos (@live-photos)**: ---
- **Mac Catalyst (@mac-catalyst)**: ---
- **Machine learning (@machine-learning)**: ---
- **Maps (@maps)**: ---
- **NFC (@nfc)**: ---
- **Photo editing (@photo-editing)**: ---
- **ResearchKit (@researchkit)**: ---
- **SharePlay (@shareplay)**: ---
- **ShazamKit (@shazamkit)**: ---
- **Sign in with Apple (@sign-in-with-apple)**: ---
- **Siri (@siri)**: ---
- **Tap to Pay on iPhone (@tap-to-pay-on-iphone)**: ---
- **VoiceOver (@voiceover)**: ---
- **Wallet (@wallet)**: ---
- **iCloud (@icloud)**: ---
- **iMessage apps and stickers (@imessage-apps-and-stickers)**: ---

### Hono
- **Hono Web Framework (@hono-web-framework)**: ---

### Hosted Agents
- **Hosted Agent Infrastructure (@hosted-agent-infrastructure)**: ---

### Hosted Agents V2 Py
- **Azure AI Hosted Agents (Python) (@azure-ai-hosted-agents-(python))**: ---

### Html Injection Testing
- **HTML Injection Testing (@html-injection-testing)**: ---

### Hubspot Automation
- **HubSpot CRM Automation via Rube MCP (@hubspot-crm-automation-via-rube-mcp)**: ---

### Hubspot Integration
- **HubSpot Integration (@hubspot-integration)**: ---

### Hugging Face Community Evals
- **Overview (@overview)**: ---
- **Usage Examples (@usage-examples)**: This document provides practical examples for **running evaluations locally** against Hugging Face Hub models.

### Hugging Face Dataset Viewer
- **Hugging Face Dataset Viewer (@hugging-face-dataset-viewer)**: ---

### Hugging Face Gradio
- **Gradio (@gradio)**: ---
- **Gradio End-to-End Examples (@gradio-end-to-end-examples)**: Complete working Gradio apps for reference.

### Hugging Face Jobs
- **Running Workloads on Hugging Face Jobs (@running-workloads-on-hugging-face-jobs)**: ---
- **Saving Results to Hugging Face Hub (@saving-results-to-hugging-face-hub)**: **⚠️ CRITICAL:** Job environments are ephemeral. ALL results are lost when a job completes unless persisted to the Hub or external storage.
- **Token Usage Guide for Hugging Face Jobs (@token-usage-guide-for-hugging-face-jobs)**: **⚠️ CRITICAL:** Proper token usage is essential for any job that interacts with the Hugging Face Hub.
- **Troubleshooting Guide (@troubleshooting-guide)**: Common issues and solutions for Hugging Face Jobs.

### Hugging Face Model Trainer
- **Common Training Patterns (@common-training-patterns)**: This guide provides common training patterns and use cases for TRL on Hugging Face Jobs.
- **GGUF Conversion Guide (@gguf-conversion-guide)**: After training models with TRL on Hugging Face Jobs, convert them to **GGUF format** for use with llama.cpp, Ollama, LM Studio, and other local inference tools.
- **Hardware Selection Guide (@hardware-selection-guide)**: Choosing the right hardware (flavor) is critical for cost-effective training.
- **Local Training on macOS (Apple Silicon) (@local-training-on-macos-(apple-silicon))**: Run small LoRA fine-tuning jobs locally on Mac for smoke tests and quick iteration before submitting to HF Jobs.
- **Reliability Principles for Training Jobs (@reliability-principles-for-training-jobs)**: These principles are derived from real production failures and successful fixes. Following them prevents common failure modes and ensures reliable job execution.
- **Saving Training Results to Hugging Face Hub (@saving-training-results-to-hugging-face-hub)**: **⚠️ CRITICAL:** Training environments are ephemeral. ALL results are lost when a job completes unless pushed to the Hub.
- **TRL Training Methods Overview (@trl-training-methods-overview)**: TRL (Transformer Reinforcement Learning) provides multiple training methods for fine-tuning and aligning language models. This reference provides a brief overview of each method.
- **TRL Training on Hugging Face Jobs (@trl-training-on-hugging-face-jobs)**: ---
- **Trackio Integration for TRL Training (@trackio-integration-for-trl-training)**: **Trackio** is an experiment tracking library that provides real-time metrics visualization for remote training on Hugging Face Jobs infrastructure.
- **Troubleshooting TRL Training Jobs (@troubleshooting-trl-training-jobs)**: Common issues and solutions when training with TRL on Hugging Face Jobs.
- **Unsloth: Fast Fine-Tuning with Memory Optimization (@unsloth:-fast-fine-tuning-with-memory-optimization)**: **Unsloth** is a fine-tuning library that provides ~2x faster training and ~60% less VRAM usage for LLM training. It's particularly useful when working with limited GPU memory or when speed is crit...

### Hugging Face Paper Publisher
- **Example Usage: HF Paper Publisher Skill (@example-usage:-hf-paper-publisher-skill)**: This document demonstrates common workflows for publishing research papers on Hugging Face Hub.
- **Quick Reference Guide (@quick-reference-guide)**: ```bash
- **{{TITLE}} (@{{title}})**: ---

### Hugging Face Papers
- **Hugging Face Paper Pages (@hugging-face-paper-pages)**: ---

### Hugging Face Tool Builder
- **Hugging Face API Tool Builder (@hugging-face-api-tool-builder)**: ---

### Hugging Face Trackio
- **Logging Metrics with Trackio (@logging-metrics-with-trackio)**: **Trackio** is a lightweight, free experiment tracking library from Hugging Face. It provides a wandb-compatible API for logging metrics with local-first design.
- **Retrieving Metrics with Trackio CLI (@retrieving-metrics-with-trackio-cli)**: The `trackio` CLI provides direct terminal access to query Trackio experiment tracking data locally without needing to start the MCP server.
- **Trackio - Experiment Tracking for ML Training (@trackio---experiment-tracking-for-ml-training)**: ---
- **Trackio Alerts (@trackio-alerts)**: Alerts let you flag important training events directly from code. They are the primary mechanism for LLM agents to diagnose runs and iterate autonomously on ML experiments.

### Hugging Face Vision Trainer
- **Fine-tuning SAM2 with HF Trainer (@fine-tuning-sam2-with-hf-trainer)**: Fine-tune SAM2.1 on a small part of the MicroMat dataset for image matting,
- **Image classification (@image-classification)**: - Load Food-101 dataset
- **Object Detection Training Reference (@object-detection-training-reference)**: - Load the CPPE-5 dataset
- **Saving Vision Models to Hugging Face Hub (@saving-vision-models-to-hugging-face-hub)**: - Why Hub Push is Required
- **Using timm models with Hugging Face Trainer (@using-timm-models-with-hugging-face-trainer)**: Transformers has first-class support for timm models via the `TimmWrapper` classes. You can load any timm model and use it directly with the `Trainer` API for image classification. Here's how it wo...
- **Vision Model Training on Hugging Face Jobs (@vision-model-training-on-hugging-face-jobs)**: ---

### Humanize Chinese
- **Humanize Chinese (@humanize-chinese)**: ---

### Hybrid Cloud Networking
- **Hybrid Cloud Networking (@hybrid-cloud-networking)**: ---

### Hybrid Search Implementation
- **Hybrid Search Implementation (@hybrid-search-implementation)**: ---
- **Hybrid Search Implementation Implementation Playbook (@hybrid-search-implementation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### I18N Localization
- **i18n & Localization (@i18n-&-localization)**: ---

### Iconsax Library
- **Iconsax Library Skill (@iconsax-library-skill)**: ---

### Idea Darwin
- **Idea Darwin Engine (@idea-darwin-engine)**: ---

### Idor Testing
- **IDOR Vulnerability Testing (@idor-vulnerability-testing)**: ---

### Ilya Sutskever
- **SKILL: Ilya Sutskever — O Místico do Deep Learning (v2.0) (@skill:-ilya-sutskever-—-o-místico-do-deep-learning-(v2.0))**: ---

### Image Studio
- **IMAGE-STUDIO: Gerador de Imagens Inteligente (@image-studio:-gerador-de-imagens-inteligente)**: ---

### Imagen
- **Imagen - AI Image Generation Skill (@imagen---ai-image-generation-skill)**: ---

### Incident Response Smart Fix
- **Intelligent Issue Resolution with Multi-Agent Orchestration (@intelligent-issue-resolution-with-multi-agent-orchestration)**: ---
- **Intelligent Issue Resolution with Multi-Agent Orchestration Implementation Playbook (@intelligent-issue-resolution-with-multi-agent-orchestration-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Incident Runbook Templates
- **Incident Runbook Templates (@incident-runbook-templates)**: ---

### Infinite Gratitude
- **Infinite Gratitude (@infinite-gratitude)**: ---

### Inngest
- **Inngest Integration (@inngest-integration)**: ---

### Instagram
- **Guia de Publicação — Specs de Mídia e Fluxos (@guia-de-publicação-—-specs-de-mídia-e-fluxos)**: | Propriedade | Requisito |
- **Instagram Graph API — Referência de Endpoints (@instagram-graph-api-—-referência-de-endpoints)**: Base URL: `https://graph.instagram.com/v21.0`
- **Permissões OAuth — Scopes por Feature (@permissões-oauth-—-scopes-por-feature)**: | Scope | Descrição | Features |
- **Rate Limits — Instagram Graph API (@rate-limits-—-instagram-graph-api)**: | Recurso | Limite | Janela | Notas |
- **Schema do Banco SQLite — instagram.db (@schema-do-banco-sqlite-—-instagram.db)**: Localização: `C:\Users\renat\skills\instagram\data\instagram.db`
- **Setup Walkthrough — Meta App e OAuth (@setup-walkthrough-—-meta-app-e-oauth)**: 1. Conta Instagram Business ou Creator
- **Skill: Instagram Integration (@skill:-instagram-integration)**: ---
- **Tipos de Conta Instagram — Business vs Creator (@tipos-de-conta-instagram-—-business-vs-creator)**: | Feature | Personal | Creator | Business |

### Instagram Automation
- **Instagram Automation via Rube MCP (@instagram-automation-via-rube-mcp)**: ---

### Interactive Portfolio
- **Interactive Portfolio (@interactive-portfolio)**: ---

### Intercom Automation
- **Intercom Automation via Rube MCP (@intercom-automation-via-rube-mcp)**: ---

### Internal Comms
- **3p-updates.md (@3p-updates.md)**: You are being asked to write a 3P update. 3P updates stand for "Progress, Plans, Problems." The main audience is for executives, leadership, other teammates, etc. They're meant to be very succinct ...
- **company-newsletter.md (@company-newsletter.md)**: You are being asked to write a company-wide newsletter update. You are meant to summarize the past week/month of a company in the form of a newsletter that the entire company will read. It should b...
- **faq-answers.md (@faq-answers.md)**: You are an assistant for answering questions that are being asked across the company. Every week, there are lots of questions that get asked across the company, and your goal is to try to summarize...
- **general-comms.md (@general-comms.md)**: You are being asked to write internal company communication that doesn't fit into the standard formats (3P

### Interview Coach
- **Interview Coach (@interview-coach)**: ---

### Inventory Demand Planning
- **Communication Templates — Inventory Demand Planning (@communication-templates-—-inventory-demand-planning)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing demand planning communications.
- **Decision Frameworks — Inventory Demand Planning (@decision-frameworks-—-inventory-demand-planning)**: This reference provides the detailed decision logic, optimization models, method selection
- **Inventory Demand Planning (@inventory-demand-planning)**: ---
- **Inventory Demand Planning — Edge Cases Reference (@inventory-demand-planning-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous demand planning situations that don't resolve through standard forecasting and replenishment workflows.

### Ios Debugger Agent
- **iOS Debugger Agent (@ios-debugger-agent)**: ---

### Istio Traffic Management
- **Istio Traffic Management (@istio-traffic-management)**: ---

### Iterate Pr
- **Iterate on PR Until CI Passes (@iterate-on-pr-until-ci-passes)**: ---

### Javascript Mastery
- **🧠 JavaScript Mastery (@🧠-javascript-mastery)**: ---

### Javascript Testing Patterns
- **JavaScript Testing Patterns (@javascript-testing-patterns)**: ---
- **JavaScript Testing Patterns Implementation Playbook (@javascript-testing-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Javascript Typescript Typescript Scaffold
- **TypeScript Project Scaffolding (@typescript-project-scaffolding)**: ---

### Jira Automation
- **Jira Automation via Rube MCP (@jira-automation-via-rube-mcp)**: ---

### Jobgpt
- **JobGPT - Job Search Automation (@jobgpt---job-search-automation)**: ---

### Jq
- **jq — JSON Querying and Transformation (@jq-—-json-querying-and-transformation)**: ---

### Json Canvas
- **JSON Canvas Complete Examples (@json-canvas-complete-examples)**: ```json
- **JSON Canvas Skill (@json-canvas-skill)**: ---

### Junta Leiloeiros
- **Base Legal para Coleta de Dados de Leiloeiros (@base-legal-para-coleta-de-dados-de-leiloeiros)**: Regulamento dos Leiloeiros Oficiais do Brasil. Estabelece que leiloeiros devem ser
- **Juntas Comerciais do Brasil — URLs e Status de Scraping (@juntas-comerciais-do-brasil-—-urls-e-status-de-scraping)**: Tabela de referência atualizada com todas as 27 Juntas Comerciais e seus sites de leiloeiros.
- **Schema de Dados — Leiloeiros das Juntas Comerciais (@schema-de-dados-—-leiloeiros-das-juntas-comerciais)**: ```sql
- **Skill: Leiloeiros das Juntas Comerciais do Brasil (@skill:-leiloeiros-das-juntas-comerciais-do-brasil)**: ---

### K6 Load Testing
- **k6 Load Testing (@k6-load-testing)**: ---

### K8S Manifest Generator
- **Kubernetes Deployment Specification Reference (@kubernetes-deployment-specification-reference)**: Comprehensive reference for Kubernetes Deployment resources, covering all key fields, best practices, and common patterns.
- **Kubernetes Manifest Generator (@kubernetes-manifest-generator)**: ---
- **Kubernetes Manifest Generator Implementation Playbook (@kubernetes-manifest-generator-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.
- **Kubernetes Service Specification Reference (@kubernetes-service-specification-reference)**: Comprehensive reference for Kubernetes Service resources, covering service types, networking, load balancing, and service discovery patterns.

### K8S Security Policies
- **Kubernetes Security Policies (@kubernetes-security-policies)**: ---
- **RBAC Patterns and Best Practices (@rbac-patterns-and-best-practices)**: ```yaml

### Kaizen
- **Kaizen: Continuous Improvement (@kaizen:-continuous-improvement)**: ---

### Keyword Extractor
- **Keyword Extractor (@keyword-extractor)**: ---

### Klaviyo Automation
- **Klaviyo Automation via Rube MCP (@klaviyo-automation-via-rube-mcp)**: ---

### Kotlin Coroutines Expert
- **Kotlin Coroutines Expert (@kotlin-coroutines-expert)**: ---

### Kpi Dashboard Design
- **KPI Dashboard Design (@kpi-dashboard-design)**: ---

### Kubernetes Deployment
- **Kubernetes Deployment Workflow (@kubernetes-deployment-workflow)**: ---

### Landing Page Generator
- **High-Converting Landing Page Patterns (@high-converting-landing-page-patterns)**: This reference catalogs proven landing page design patterns that drive higher conversion rates. Each pattern includes placement guidance, implementation notes, and A/B testing priorities.
- **Landing Page Copywriting Frameworks (@landing-page-copywriting-frameworks)**: Four copy frameworks with worked SaaS examples you can adapt. Each framework includes a complete before/after example plus specific guidelines for each section.
- **Landing Page Generator (@landing-page-generator)**: ---
- **Landing Page Patterns (@landing-page-patterns)**: This reference captures high-converting page patterns and copy structures.
- **Landing Page SEO Checklist (@landing-page-seo-checklist)**: This checklist ensures landing pages are optimized for search engine visibility while maintaining conversion focus. Apply these checks before launching any landing page.

### Langchain Architecture
- **LangChain Architecture (@langchain-architecture)**: ---

### Langfuse
- **Langfuse (@langfuse)**: ---

### Langgraph
- **LangGraph (@langgraph)**: ---

### Laravel Expert
- **Laravel Expert (@laravel-expert)**: ---

### Laravel Security Audit
- **Laravel Security Audit (@laravel-security-audit)**: ---

### Last30Days
- **feat: Add WebSearch as Third Source (Zero-Config Fallback) (@feat:-add-websearch-as-third-source-(zero-config-fallback))**: Add Claude's built-in WebSearch tool as a third research source for `/last30days`. This enables the skill to work **out of the box with zero API keys** while preserving the primacy of Reddit/X as t...
- **fix: Enforce Strict 30-Day Date Filtering (@fix:-enforce-strict-30-day-date-filtering)**: The `/last30days` skill is returning content older than 30 days, violating its core promise. Analysis shows:
- **last30days Implementation Tasks (@last30days-implementation-tasks)**: - [x] Create directory structure
- **last30days Skill Specification (@last30days-skill-specification)**: `last30days` is a Claude Code skill that researches a given topic across Reddit and X (Twitter) using the OpenAI Responses API and xAI Responses API respectively. It enforces a strict 30-day recenc...
- **last30days: Research Any Topic from the Last 30 Days (@last30days:-research-any-topic-from-the-last-30-days)**: ---

### Latex Paper Conversion
- **LaTeX Paper Conversion (@latex-paper-conversion)**: ---

### Launch Strategy
- **Launch Strategy (@launch-strategy)**: ---

### Lead Magnets
- **Lead Magnet Benchmarks (@lead-magnet-benchmarks)**: Reference data for planning and evaluating lead magnet performance.
- **Lead Magnet Format Guide (@lead-magnet-format-guide)**: Detailed creation guidance for each lead magnet format.
- **Lead Magnets (@lead-magnets)**: ---

### Leiloeiro Avaliacao
- **Fontes e Referências — Leiloeiro Avaliação (@fontes-e-referências-—-leiloeiro-avaliação)**: - ABNT NBR 14653-1:2019 — Procedimentos gerais
- **SKILL DE AVALIAÇÃO DE IMÓVEL — PERITO AVALIADOR (@skill-de-avaliação-de-imóvel-—-perito-avaliador)**: ---

### Leiloeiro Edital
- **Fontes e Referências — Leiloeiro Edital (@fontes-e-referências-—-leiloeiro-edital)**: - CPC/2015 — Arts. 887-903 (Edital e Arrematação)
- **SKILL DE EDITAL — ANÁLISE PERICIAL DE EDITAIS DE LEILÃO (@skill-de-edital-—-análise-pericial-de-editais-de-leilão)**: ---

### Leiloeiro Ia
- **Fontes e Referências — Leiloeiro IA (@fontes-e-referências-—-leiloeiro-ia)**: - CPC/2015 (Lei 13.105/2015) — Execução Civil (Arts. 774-925)
- **LEILOEIRO JURÍDICO, PERICIAL E DE MERCADO — IA (@leiloeiro-jurídico,-pericial-e-de-mercado-—-ia)**: ---

### Leiloeiro Juridico
- **Fontes e Referências — Leiloeiro Jurídico (@fontes-e-referências-—-leiloeiro-jurídico)**: - CPC/2015 (Lei 13.105/2015) — Arts. 774-925 (Execução)
- **SKILL JURÍDICA — LEILÕES DE IMÓVEIS (@skill-jurídica-—-leilões-de-imóveis)**: ---

### Leiloeiro Mercado
- **Fontes e Referências — Leiloeiro Mercado (@fontes-e-referências-—-leiloeiro-mercado)**: - ZAP Imóveis (zapimoveis.com.br)
- **SKILL DE MERCADO — ANALISTA DE ATIVOS IMOBILIÁRIOS EM LEILÃO (@skill-de-mercado-—-analista-de-ativos-imobiliários-em-leilão)**: ---

### Leiloeiro Risco
- **Fontes e Referências — Leiloeiro Risco (@fontes-e-referências-—-leiloeiro-risco)**: - CPC/2015 — Arts. 829-925 (Execução e Arrematação)
- **SKILL DE RISCO — AUDITOR DE RISCO EM LEILÕES (@skill-de-risco-—-auditor-de-risco-em-leilões)**: ---

### Lex
- **Business Foundation & Governance Templates (@business-foundation-&-governance-templates)**: ---
- **Employment & Workforce Templates (@employment-&-workforce-templates)**: ---
- **Intellectual Property (IP) Templates (@intellectual-property-(ip)-templates)**: ---
- **LEX — Findings & Research (@lex-—-findings-&-research)**: * The application must cover 29 specific jurisdictions (USA, Canada, +27 EU Member States).
- **LEX: Legal-Entity-X-ref (@lex:-legal-entity-x-ref)**: ---
- **Real Estate & Facilities Templates (@real-estate-&-facilities-templates)**: ---
- **Sales & Commercial Transactions Templates (@sales-&-commercial-transactions-templates)**: ---

### Libreoffice
- **LibreOffice Base (@libreoffice-base)**: ---
- **LibreOffice Calc (@libreoffice-calc)**: ---
- **LibreOffice Draw (@libreoffice-draw)**: ---
- **LibreOffice Impress (@libreoffice-impress)**: ---
- **LibreOffice Writer (@libreoffice-writer)**: ---

### Linear Automation
- **Linear Automation via Rube MCP (@linear-automation-via-rube-mcp)**: ---

### Linear Claude Skill
- **Linear (@linear)**: ---

### Linkedin Automation
- **LinkedIn Automation via Rube MCP (@linkedin-automation-via-rube-mcp)**: ---

### Linkedin Cli
- **LinkedIn Skill (@linkedin-skill)**: ---

### Linkerd Patterns
- **Linkerd Patterns (@linkerd-patterns)**: ---

### Lint And Validate
- **Lint and Validate Skill (@lint-and-validate-skill)**: ---

### Linux Privilege Escalation
- **Linux Privilege Escalation (@linux-privilege-escalation)**: ---

### Linux Shell Scripting
- **Linux Production Shell Scripts (@linux-production-shell-scripts)**: ---

### Linux Troubleshooting
- **Linux Troubleshooting Workflow (@linux-troubleshooting-workflow)**: ---

### Llm App Patterns
- **🤖 LLM Application Patterns (@🤖-llm-application-patterns)**: ---

### Llm Application Dev Ai Assistant
- **AI Assistant Development (@ai-assistant-development)**: ---
- **AI Assistant Development Implementation Playbook (@ai-assistant-development-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Llm Application Dev Langchain Agent
- **LangChain/LangGraph Agent Development Expert (@langchain/langgraph-agent-development-expert)**: ---

### Llm Application Dev Prompt Optimize
- **Prompt Optimization (@prompt-optimization)**: ---
- **Prompt Optimization Implementation Playbook (@prompt-optimization-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Llm Evaluation
- **LLM Evaluation (@llm-evaluation)**: ---

### Llm Ops
- **LLM-OPS -- IA de Producao (@llm-ops----ia-de-producao)**: ---

### Llm Prompt Optimizer
- **LLM Prompt Optimizer (@llm-prompt-optimizer)**: ---

### Llm Structured Output
- **LLM Structured Output (@llm-structured-output)**: ---

### Local Legal Seo Audit
- **Local Legal SEO Audit (@local-legal-seo-audit)**: ---

### Logistics Exception Management
- **Communication Templates — Logistics Exception Management (@communication-templates-—-logistics-exception-management)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing exception communications.
- **Decision Frameworks — Logistics Exception Management (@decision-frameworks-—-logistics-exception-management)**: This reference provides the detailed decision logic, scoring matrices, financial models,
- **Logistics Exception Management (@logistics-exception-management)**: ---
- **Logistics Exception Management — Edge Cases Reference (@logistics-exception-management-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous exceptions that don't resolve through standard workflows.

### Loki Mode
- **Acknowledgements (@acknowledgements)**: Loki Mode stands on the shoulders of giants. This project incorporates research, patterns, and insights from the leading AI labs, academic institutions, and practitioners in the field.
- **Advanced Agentic Patterns Reference (@advanced-agentic-patterns-reference)**: Research-backed patterns from 2025-2026 literature for enhanced multi-agent orchestration.
- **Agent Type Definitions (@agent-type-definitions)**: Complete specifications for all 37 specialized agent types in the Loki Mode multi-agent system.
- **Agent Types Reference (@agent-types-reference)**: Complete definitions and capabilities for all 37 specialized agent types.
- **Business Operations Reference (@business-operations-reference)**: Workflows and procedures for business swarm agents.
- **Changelog (@changelog)**: All notable changes to Loki Mode will be documented in this file.
- **Core Workflow Reference (@core-workflow-reference)**: Full RARV cycle, CONTINUITY.md template, and autonomy rules.
- **Deployment Reference (@deployment-reference)**: Infrastructure provisioning and deployment instructions for all supported platforms.
- **End-to-End (E2E) Verification Report (@end-to-end-(e2e)-verification-report)**: **Task ID:** task-018 (eng-qa e2e-test)
- **Lab Research Patterns Reference (@lab-research-patterns-reference)**: Research-backed patterns from Google DeepMind and Anthropic for enhanced multi-agent orchestration and safety.
- **Loki Mode - Claude Code Skill (@loki-mode---claude-code-skill)**: Multi-agent autonomous startup system for Claude Code. Takes PRD to fully deployed, revenue-generating product with zero human intervention.
- **Loki Mode - Conversation Context Export (@loki-mode---conversation-context-export)**: **Date:** 2025-12-28
- **Loki Mode - Multi-Agent Autonomous Startup System (@loki-mode---multi-agent-autonomous-startup-system)**: ---
- **Loki Mode Agent Constitution (@loki-mode-agent-constitution)**: > **Machine-Enforceable Behavioral Contract for All Agents**
- **Loki Mode Benchmark Results (@loki-mode-benchmark-results)**: **Generated:** 2026-01-05 14:15:24
- **Loki Mode Competitive Analysis (@loki-mode-competitive-analysis)**: *Last Updated: 2026-01-05*
- **Loki Mode Installation Guide (@loki-mode-installation-guide)**: Complete installation instructions for all platforms and use cases.
- **Loki Mode Test Execution Report (@loki-mode-test-execution-report)**: - **Test Date:** 2026-01-02
- **Loki Mode Voice-Over Script (@loki-mode-voice-over-script)**: Complete narration for Loki Mode demo video.
- **Loki Mode Working Memory (@loki-mode-working-memory)**: Last Updated: 2026-01-02T23:55:00Z
- **Memory System Reference (@memory-system-reference)**: Enhanced memory architecture based on 2025 research (MIRIX, A-Mem, MemGPT, AriGraph).
- **OpenAI Agent Patterns Reference (@openai-agent-patterns-reference)**: Research-backed patterns from OpenAI's Agents SDK, Deep Research, and autonomous agent frameworks.
- **PRD: Full-Stack Demo App (@prd:-full-stack-demo-app)**: A complete full-stack application demonstrating Loki Mode's end-to-end capabilities. A simple bookmark manager with tags.
- **PRD: REST API Service (@prd:-rest-api-service)**: A simple REST API for managing notes. Tests Loki Mode's backend-only capabilities.
- **PRD: Simple Todo App (@prd:-simple-todo-app)**: A minimal todo application for testing Loki Mode with a simple, well-defined scope.
- **PRD: Static Landing Page (@prd:-static-landing-page)**: A simple static landing page for a fictional SaaS product. Tests Loki Mode's frontend and marketing agent capabilities.
- **Production Patterns Reference (@production-patterns-reference)**: Practitioner-tested patterns from Hacker News discussions and real-world deployments. These patterns represent what actually works in production, not theoretical frameworks.
- **Quality Control Reference (@quality-control-reference)**: Quality gates, code review process, and severity blocking rules.
- **SDLC Phases Reference (@sdlc-phases-reference)**: All phases with detailed workflows and testing procedures.
- **Task 018: E2E Manual Testing Verification - COMPLETED (@task-018:-e2e-manual-testing-verification---completed)**: **Task ID:** task-018
- **Task 018: E2E Testing Documentation (@task-018:-e2e-testing-documentation)**: This directory contains comprehensive testing and verification documentation for the Loki Mode autonomous Todo application project.
- **Task Queue Reference (@task-queue-reference)**: Distributed task queue system, dead letter handling, and circuit breakers.
- **Tool Orchestration Patterns Reference (@tool-orchestration-patterns-reference)**: Research-backed patterns inspired by NVIDIA ToolOrchestra, OpenAI Agents SDK, and multi-agent coordination research.
- **Vibe Kanban Integration (@vibe-kanban-integration)**: Loki Mode can optionally integrate with [Vibe Kanban](https://github.com/BloopAI/vibe-kanban) to provide a visual dashboard for monitoring autonomous execution.

### M365 Agents Dotnet
- **Microsoft 365 Agents SDK (.NET) (@microsoft-365-agents-sdk-(.net))**: ---

### M365 Agents Py
- **Microsoft 365 Agents SDK (Python) (@microsoft-365-agents-sdk-(python))**: ---

### M365 Agents Ts
- **Microsoft 365 Agents SDK (TypeScript) (@microsoft-365-agents-sdk-(typescript))**: ---

### Machine Learning Ops Ml Pipeline
- **Machine Learning Pipeline - Multi-Agent MLOps Orchestration (@machine-learning-pipeline---multi-agent-mlops-orchestration)**: ---

### Macos Menubar Tuist App
- **macos-menubar-tuist-app (@macos-menubar-tuist-app)**: ---

### Macos Spm App Packaging
- **Packaging notes (@packaging-notes)**: SwiftPM places binaries under:
- **Release and notarization notes (@release-and-notarization-notes)**: - Install Xcode Command Line Tools (for `xcrun` and `notarytool`).
- **Scaffold a SwiftPM macOS app (no Xcode) (@scaffold-a-swiftpm-macos-app-(no-xcode))**: 1) Create a repo and initialize SwiftPM:
- **macOS SwiftPM App Packaging (No Xcode) (@macos-swiftpm-app-packaging-(no-xcode))**: ---

### Magic Animator
- **Magic Animator Skill (@magic-animator-skill)**: ---

### Magic Ui Generator
- **Magic UI Generator (@magic-ui-generator)**: ---

### Mailchimp Automation
- **Mailchimp Automation via Rube MCP (@mailchimp-automation-via-rube-mcp)**: ---

### Make Automation
- **Make Automation via Rube MCP (@make-automation-via-rube-mcp)**: ---

### Makepad Animation
- **Makepad Animation Skill (@makepad-animation-skill)**: ---

### Makepad Basics
- **Makepad Basics Skill (@makepad-basics-skill)**: ---

### Makepad Deployment
- **Makepad Packaging & Deployment (@makepad-packaging-&-deployment)**: ---

### Makepad Dsl
- **Makepad DSL Skill (@makepad-dsl-skill)**: ---

### Makepad Event Action
- **Makepad Event/Action Skill (@makepad-event/action-skill)**: ---

### Makepad Font
- **Makepad Font Skill (@makepad-font-skill)**: ---

### Makepad Layout
- **Makepad Layout Skill (@makepad-layout-skill)**: ---

### Makepad Platform
- **Makepad Platform Skill (@makepad-platform-skill)**: ---

### Makepad Reference
- **Makepad Reference (@makepad-reference)**: ---

### Makepad Shaders
- **Makepad Shaders Skill (@makepad-shaders-skill)**: ---

### Makepad Skills
- **Makepad Skills (@makepad-skills)**: ---

### Makepad Splash
- **Makepad Splash Skill (@makepad-splash-skill)**: ---

### Makepad Widgets
- **Makepad Widgets Skill (@makepad-widgets-skill)**: ---

### Malware Analyst
- **File identification (@file-identification)**: ---

### Manage Skills
- **Manage AI Agent Skills (@manage-ai-agent-skills)**: ---

### Manifest
- **Manifest Setup (@manifest-setup)**: ---

### Market Sizing Analysis
- **Market Sizing Analysis (@market-sizing-analysis)**: ---
- **Market Sizing Data Sources (@market-sizing-data-sources)**: Curated list of credible sources for market research and sizing analysis.
- **SaaS Market Sizing Example: AI-Powered Email Marketing for E-Commerce (@saas-market-sizing-example:-ai-powered-email-marketing-for-e-commerce)**: Complete TAM/SAM/SOM calculation for a B2B SaaS startup using bottom-up and top-down methodologies.

### Marketing Ideas
- **Marketing Ideas for SaaS (with Feasibility Scoring) (@marketing-ideas-for-saas-(with-feasibility-scoring))**: ---

### Marketing Psychology
- **Marketing Psychology & Mental Models (@marketing-psychology-&-mental-models)**: ---

### Matematico Tao
- **Auri/EarLLM — Contexto Completo para Análise Matemática (@auri/earllm-—-contexto-completo-para-análise-matemática)**: **Projeto**: Auri v2.5.0 (EarLLM One)
- **Modelos Formais de Concorrência para Kotlin/Android (@modelos-formais-de-concorrência-para-kotlin/android)**: Um processo CSP é definido por:
- **Padrões de Complexidade em Android/Kotlin (@padrões-de-complexidade-em-android/kotlin)**: ```
- **Prof. Euler — Matemático Ultra-Avançado (@prof.-euler-—-matemático-ultra-avançado)**: ---
- **Teoria da Informação Aplicada a Código e Sistemas (@teoria-da-informação-aplicada-a-código-e-sistemas)**: ```

### Matplotlib
- **Matplotlib (@matplotlib)**: ---

### Maxia
- **MAXIA — AI-to-AI Marketplace on Solana (@maxia-—-ai-to-ai-marketplace-on-solana)**: ---

### Mcp Builder
- **MCP Server Best Practices (@mcp-server-best-practices)**: - **Python**: `{service}_mcp` (e.g., `slack_mcp`)
- **MCP Server Evaluation Guide (@mcp-server-evaluation-guide)**: This document provides guidance on creating comprehensive evaluations for MCP servers. Evaluations test whether LLMs can effectively use your MCP server to answer realistic, complex questions using...
- **Node/TypeScript MCP Server Implementation Guide (@node/typescript-mcp-server-implementation-guide)**: This document provides Node/TypeScript-specific best practices and examples for implementing MCP servers using the MCP TypeScript SDK. It covers project structure, server setup, tool registration p...
- **Python MCP Server Implementation Guide (@python-mcp-server-implementation-guide)**: This document provides Python-specific best practices and examples for implementing MCP servers using the MCP Python SDK. It covers server setup, tool registration patterns, input validation with P...

### Mcp Builder Ms
- **MCP Server Development Guide (@mcp-server-development-guide)**: ---

### Memory Forensics
- **Memory Forensics (@memory-forensics)**: ---

### Memory Safety Patterns
- **Memory Safety Patterns (@memory-safety-patterns)**: ---
- **Memory Safety Patterns Implementation Playbook (@memory-safety-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Memory Systems
- **Memory System Design (@memory-system-design)**: ---

### Mental Health Analyzer
- **心理健康分析技能 (@心理健康分析技能)**: ---

### Metasploit Framework
- **Metasploit Framework (@metasploit-framework)**: ---

### Micro Saas Launcher
- **Micro-SaaS Launcher (@micro-saas-launcher)**: ---

### Microservices Patterns
- **Microservices Patterns (@microservices-patterns)**: ---
- **Microservices Patterns Implementation Playbook (@microservices-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Microsoft Azure Webjobs Extensions Authentication Events Dotnet
- **Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents (.NET) (@microsoft.azure.webjobs.extensions.authenticationevents-(.net))**: ---

### Microsoft Teams Automation
- **Microsoft Teams Automation via Rube MCP (@microsoft-teams-automation-via-rube-mcp)**: ---

### Miro Automation
- **Miro Automation via Rube MCP (@miro-automation-via-rube-mcp)**: ---

### Mixpanel Automation
- **Mixpanel Automation via Rube MCP (@mixpanel-automation-via-rube-mcp)**: ---

### Ml Pipeline Workflow
- **ML Pipeline Workflow (@ml-pipeline-workflow)**: ---

### Mobile Design
- **Android Platform Guidelines (@android-platform-guidelines)**: > Material Design 3 essentials, Android design conventions, Roboto typography, and native patterns.
- **Mobile Backend Patterns (@mobile-backend-patterns)**: > **This file covers backend/API patterns SPECIFIC to mobile clients.**
- **Mobile Color System Reference (@mobile-color-system-reference)**: > OLED optimization, dark mode, battery-aware colors, and outdoor visibility.
- **Mobile Debugging Guide (@mobile-debugging-guide)**: > **Stop console.log() debugging!**
- **Mobile Decision Trees (@mobile-decision-trees)**: > Framework selection, state management, storage strategy, and context-based decisions.
- **Mobile Design System (@mobile-design-system)**: ---
- **Mobile Design Thinking (@mobile-design-thinking)**: > **This file prevents AI from using memorized patterns and forces genuine thinking.**
- **Mobile Navigation Reference (@mobile-navigation-reference)**: > Navigation patterns, deep linking, back handling, and tab/stack/drawer decisions.
- **Mobile Performance Reference (@mobile-performance-reference)**: > Deep dive into React Native and Flutter performance optimization, 60fps animations, memory management, and battery considerations.
- **Mobile Testing Patterns (@mobile-testing-patterns)**: > **Mobile testing is NOT web testing. Different constraints, different strategies.**
- **Mobile Typography Reference (@mobile-typography-reference)**: > Type scale, system fonts, Dynamic Type, accessibility, and dark mode typography.
- **Touch Psychology Reference (@touch-psychology-reference)**: > Deep dive into mobile touch interaction, Fitts' Law for touch, thumb zone anatomy, gesture psychology, and haptic feedback.
- **iOS Platform Guidelines (@ios-platform-guidelines)**: > Human Interface Guidelines (HIG) essentials, iOS design conventions, SF Pro typography, and native patterns.

### Modern Javascript Patterns
- **Modern JavaScript Patterns (@modern-javascript-patterns)**: ---
- **Modern JavaScript Patterns Implementation Playbook (@modern-javascript-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Molykit
- **MolyKit Skill (@molykit-skill)**: ---

### Monday Automation
- **Monday.com Automation via Rube MCP (@monday.com-automation-via-rube-mcp)**: ---

### Monetization
- **MONETIZATION - Do Produto ao Revenue (@monetization---do-produto-ao-revenue)**: ---

### Monorepo Architect
- **Monorepo Architect (@monorepo-architect)**: ---

### Monorepo Management
- **Monorepo Management (@monorepo-management)**: ---
- **Monorepo Management Implementation Playbook (@monorepo-management-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Monte Carlo Monitor Creation
- **Comparison Monitor Reference (@comparison-monitor-reference)**: Detailed reference for building `createComparisonMonitorMac` tool calls.
- **Custom SQL Monitor Reference (@custom-sql-monitor-reference)**: Detailed reference for building `createCustomSqlMonitorMac` tool calls.
- **Metric Monitor Reference (@metric-monitor-reference)**: Detailed reference for building `createMetricMonitorMac` tool calls.
- **Monte Carlo Monitor Creation Skill (@monte-carlo-monitor-creation-skill)**: ---
- **Table Monitor Reference (@table-monitor-reference)**: Detailed reference for building `createTableMonitorMac` tool calls.
- **Validation Monitor Reference (@validation-monitor-reference)**: Detailed reference for building `createValidationMonitorMac` tool calls.

### Monte Carlo Prevent
- **MCP Parameter Notes (@mcp-parameter-notes)**: Important parameter details for Monte Carlo MCP tools. Consult when making API
- **Monte Carlo Prevent Skill (@monte-carlo-prevent-skill)**: ---
- **Verify the server is reachable (@verify-the-server-is-reachable)**: ```bash
- **Workflow Details (@workflow-details)**: Detailed step-by-step instructions for each Monte Carlo Prevent workflow.

### Monte Carlo Push Ingestion
- **Anomaly Detection for Push-Ingested Data (@anomaly-detection-for-push-ingested-data)**: Push volume and freshness data feeds the same anomaly detectors as the pull model.
- **Custom Lineage Nodes and Edges (@custom-lineage-nodes-and-edges)**: The `send_lineage()` pycarlo method is the right choice for warehouse tables you own.
- **Direct HTTP API (without pycarlo) (@direct-http-api-(without-pycarlo))**: The `pycarlo` SDK is optional. You can call the push APIs directly over HTTPS from any
- **Monte Carlo Push Ingestion (@monte-carlo-push-ingestion)**: ---
- **Prerequisites (@prerequisites)**: Push ingestion requires **two separate Monte Carlo API keys** — one for pushing data, one
- **Pushing Query Logs (@pushing-query-logs)**: Query logs let Monte Carlo build table usage history, populate query lineage, and surface
- **Pushing Table Metadata (@pushing-table-metadata)**: Metadata push sends three types of signals per table:
- **Pushing Table and Column Lineage (@pushing-table-and-column-lineage)**: Both table-level and column-level lineage use the same endpoint: `POST /ingest/v1/lineage`.
- **Validating Pushed Data (@validating-pushed-data)**: All verification queries use the **GraphQL API key** at `https://api.getmontecarlo.com/graphql`.

### Monte Carlo Validation Notebook
- **Setup (@setup)**: ---

### Moodle External Api Development
- **Moodle External API Development (@moodle-external-api-development)**: ---

### Moyu
- **Moyu (@moyu)**: ---

### Mtls Configuration
- **mTLS Configuration (@mtls-configuration)**: ---

### Multi Advisor
- **MULTI-ADVISOR: Board de Especialistas em Paralelo (@multi-advisor:-board-de-especialistas-em-paralelo)**: ---

### Multi Agent Brainstorming
- **Multi-Agent Brainstorming (Structured Design Review) (@multi-agent-brainstorming-(structured-design-review))**: ---

### Multi Agent Patterns
- **Multi-Agent Architecture Patterns (@multi-agent-architecture-patterns)**: ---

### Multi Agent Task Orchestrator
- **Multi-Agent Task Orchestrator (@multi-agent-task-orchestrator)**: ---

### Multi Cloud Architecture
- **Multi-Cloud Architecture (@multi-cloud-architecture)**: ---

### Multi Platform Apps Multi Platform
- **Multi-Platform Feature Development Workflow (@multi-platform-feature-development-workflow)**: ---

### N8N Code Javascript
- **JavaScript Code Node (@javascript-code-node)**: ---

### N8N Code Python
- **Python Code Node (Beta) (@python-code-node-(beta))**: ---

### N8N Expression Syntax
- **n8n Expression Syntax (@n8n-expression-syntax)**: ---

### N8N Mcp Tools Expert
- **n8n MCP Tools Expert (@n8n-mcp-tools-expert)**: ---

### N8N Node Configuration
- **n8n Node Configuration (@n8n-node-configuration)**: ---

### N8N Validation Expert
- **n8n Validation Expert (@n8n-validation-expert)**: ---

### N8N Workflow Patterns
- **n8n Workflow Patterns (@n8n-workflow-patterns)**: ---

### Nanobanana Ppt Skills
- **Nanobanana Ppt Skills (@nanobanana-ppt-skills)**: ---

### Native Data Fetching
- **Expo Networking (@expo-networking)**: ---

### Neon Postgres
- **Neon Postgres (@neon-postgres)**: ---

### Nerdzao Elite
- **@nerdzao-elite (@@nerdzao-elite)**: ---

### Nerdzao Elite Gemini High
- **@nerdzao-elite-gemini-high (@@nerdzao-elite-gemini-high)**: ---

### Nestjs Expert
- **Nest.js Expert (@nest.js-expert)**: ---

### Network 101
- **Network 101 (@network-101)**: ---

### Networkx
- **NetworkX (@networkx)**: ---

### New Rails Project
- **Tech Stack (@tech-stack)**: ---

### Nextjs App Router Patterns
- **Next.js App Router Patterns (@next.js-app-router-patterns)**: ---
- **Next.js App Router Patterns Implementation Playbook (@next.js-app-router-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Nextjs Best Practices
- **Next.js Best Practices (@next.js-best-practices)**: ---

### Nextjs Supabase Auth
- **Next.js + Supabase Auth (@next.js-+-supabase-auth)**: ---

### Nft Standards
- **NFT Standards (@nft-standards)**: ---

### Nodejs Backend Patterns
- **Node.js Backend Patterns (@node.js-backend-patterns)**: ---
- **Node.js Backend Patterns Implementation Playbook (@node.js-backend-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Nodejs Best Practices
- **Node.js Best Practices (@node.js-best-practices)**: ---

### Nosql Expert
- **NoSQL Expert Patterns (Cassandra & DynamoDB) (@nosql-expert-patterns-(cassandra-&-dynamodb))**: ---

### Notebooklm
- **Authentication Architecture (@authentication-architecture)**: This skill uses a **hybrid authentication approach** that combines the best of both worlds:
- **NotebookLM Research Assistant Skill (@notebooklm-research-assistant-skill)**: ---
- **NotebookLM Skill API Reference (@notebooklm-skill-api-reference)**: Complete API documentation for all NotebookLM skill modules.
- **NotebookLM Skill Troubleshooting Guide (@notebooklm-skill-troubleshooting-guide)**: | Error | Solution |
- **NotebookLM Skill Usage Patterns (@notebooklm-skill-usage-patterns)**: Advanced patterns for using the NotebookLM skill effectively.

### Notion Automation
- **Notion Automation via Rube MCP (@notion-automation-via-rube-mcp)**: ---

### Notion Template Business
- **Notion Template Business (@notion-template-business)**: ---

### Nutrition Analyzer
- **营养分析器技能 (@营养分析器技能)**: ---

### Nx Workspace Patterns
- **Nx Workspace Patterns (@nx-workspace-patterns)**: ---

### Observability Monitoring Monitor Setup
- **Monitoring and Observability Setup (@monitoring-and-observability-setup)**: ---
- **Monitoring and Observability Setup Implementation Playbook (@monitoring-and-observability-setup-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Observability Monitoring Slo Implement
- **SLO Implementation Guide (@slo-implementation-guide)**: ---
- **SLO Implementation Guide Implementation Playbook (@slo-implementation-guide-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Obsidian Bases
- **Functions Reference (@functions-reference)**: | Function | Signature | Description |
- **Obsidian Bases Skill (@obsidian-bases-skill)**: ---

### Obsidian Cli
- **Obsidian CLI (@obsidian-cli)**: ---

### Obsidian Clipper Template Creator
- **Analysis Workflow: Validating Variables (@analysis-workflow:-validating-variables)**: To ensure your template works correctly, you must validate that the target page actually contains the data you want to extract.
- **Obsidian Web Clipper Filters (@obsidian-web-clipper-filters)**: **Official Docs:** [help.obsidian.md/web-clipper/filters](https://help.obsidian.md/web-clipper/filters)
- **Obsidian Web Clipper JSON Schema (@obsidian-web-clipper-json-schema)**: The Obsidian Web Clipper imports templates via JSON files.
- **Obsidian Web Clipper Template Creator (@obsidian-web-clipper-template-creator)**: ---
- **Obsidian Web Clipper Template Logic (@obsidian-web-clipper-template-logic)**: **Official docs:** [Logic - Obsidian Help](https://help.obsidian.md/web-clipper/logic)
- **Obsidian Web Clipper Variables (@obsidian-web-clipper-variables)**: **Official Docs:** [help.obsidian.md/web-clipper/variables](https://help.obsidian.md/web-clipper/variables)
- **Working with Obsidian Bases (@working-with-obsidian-bases)**: The user maintains "Bases" in `Bases/*.base` which define the schema and properties for different types of notes (e.g., Recipes, Clippings, People).

### Obsidian Markdown
- **Callouts Reference (@callouts-reference)**: ```markdown
- **Embeds Reference (@embeds-reference)**: ```markdown
- **Obsidian Flavored Markdown Skill (@obsidian-flavored-markdown-skill)**: ---
- **Properties (Frontmatter) Reference (@properties-(frontmatter)-reference)**: Properties use YAML frontmatter at the start of a note:

### Occupational Health Analyzer
- **职业健康分析技能 (@职业健康分析技能)**: ---

### Odoo Accounting Setup
- **Odoo Accounting Setup (@odoo-accounting-setup)**: ---

### Odoo Automated Tests
- **Odoo Automated Tests (@odoo-automated-tests)**: ---

### Odoo Backup Strategy
- **Odoo Backup Strategy (@odoo-backup-strategy)**: ---

### Odoo Docker Deployment
- **Odoo Docker Deployment (@odoo-docker-deployment)**: ---

### Odoo Ecommerce Configurator
- **Odoo eCommerce Configurator (@odoo-ecommerce-configurator)**: ---

### Odoo Edi Connector
- **Odoo EDI Connector (@odoo-edi-connector)**: ---

### Odoo Hr Payroll Setup
- **Odoo HR & Payroll Setup (@odoo-hr-&-payroll-setup)**: ---

### Odoo Inventory Optimizer
- **Odoo Inventory Optimizer (@odoo-inventory-optimizer)**: ---

### Odoo L10N Compliance
- **Odoo Localization & Compliance (l10n) (@odoo-localization-&-compliance-(l10n))**: ---

### Odoo Manufacturing Advisor
- **Odoo Manufacturing Advisor (@odoo-manufacturing-advisor)**: ---

### Odoo Migration Helper
- **Odoo Migration Helper (@odoo-migration-helper)**: ---

### Odoo Module Developer
- **Odoo Module Developer (@odoo-module-developer)**: ---

### Odoo Orm Expert
- **Odoo ORM Expert (@odoo-orm-expert)**: ---

### Odoo Performance Tuner
- **Odoo Performance Tuner (@odoo-performance-tuner)**: ---

### Odoo Project Timesheet
- **Odoo Project & Timesheet (@odoo-project-&-timesheet)**: ---

### Odoo Purchase Workflow
- **Odoo Purchase Workflow (@odoo-purchase-workflow)**: ---

### Odoo Qweb Templates
- **Odoo QWeb Templates (@odoo-qweb-templates)**: ---

### Odoo Rpc Api
- **Odoo RPC API (@odoo-rpc-api)**: ---

### Odoo Sales Crm Expert
- **Odoo Sales & CRM Expert (@odoo-sales-&-crm-expert)**: ---

### Odoo Security Rules
- **Odoo Security Rules (@odoo-security-rules)**: ---

### Odoo Shopify Integration
- **Odoo ↔ Shopify Integration (@odoo-↔-shopify-integration)**: ---

### Odoo Upgrade Advisor
- **Odoo Upgrade Advisor (@odoo-upgrade-advisor)**: ---

### Odoo Woocommerce Bridge
- **Odoo ↔ WooCommerce Bridge (@odoo-↔-woocommerce-bridge)**: ---

### Odoo Xml Views Builder
- **Odoo XML Views Builder (@odoo-xml-views-builder)**: ---

### Office Productivity
- **Office Productivity Workflow Bundle (@office-productivity-workflow-bundle)**: ---

### On Call Handoff Patterns
- **On-Call Handoff Patterns (@on-call-handoff-patterns)**: ---

### Onboarding Cro
- **Onboarding CRO (@onboarding-cro)**: ---

### One Drive Automation
- **OneDrive Automation via Rube MCP (@onedrive-automation-via-rube-mcp)**: ---

### Openapi Spec Generation
- **OpenAPI Spec Generation (@openapi-spec-generation)**: ---
- **OpenAPI Spec Generation Implementation Playbook (@openapi-spec-generation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Openclaw Github Repo Commander
- **OpenClaw GitHub Repo Commander (@openclaw-github-repo-commander)**: ---

### Oral Health Analyzer
- **口腔健康分析技能 (@口腔健康分析技能)**: ---

### Orchestrate Batch Refactor
- **Agent Prompt Templates (@agent-prompt-templates)**: Use these templates when spawning sub-agents.
- **Orchestrate Batch Refactor (@orchestrate-batch-refactor)**: ---
- **Work Packet Template (@work-packet-template)**: Use this template to define each packet before spawning workers.

### Os Scripting
- **OS/Shell Scripting Troubleshooting Workflow Bundle (@os/shell-scripting-troubleshooting-workflow-bundle)**: ---

### Oss Hunter
- **OSS Hunter 🎯 (@oss-hunter-🎯)**: ---

### Outlook Automation
- **Outlook Automation via Rube MCP (@outlook-automation-via-rube-mcp)**: ---

### Outlook Calendar Automation
- **Outlook Calendar Automation via Rube MCP (@outlook-calendar-automation-via-rube-mcp)**: ---

### Page Cro
- **Page Conversion Rate Optimization (CRO) (@page-conversion-rate-optimization-(cro))**: ---

### Pagerduty Automation
- **PagerDuty Automation via Rube MCP (@pagerduty-automation-via-rube-mcp)**: ---

### Paid Ads
- **Paid Ads (@paid-ads)**: ---

### Pakistan Payments Stack
- **Pakistan Payments Stack for SaaS (@pakistan-payments-stack-for-saas)**: ---

### Parallel Agents
- **Native Parallel Agents (@native-parallel-agents)**: ---

### Paypal Integration
- **PayPal Integration (@paypal-integration)**: ---

### Paywall Upgrade Cro
- **Paywall and Upgrade Screen CRO (@paywall-and-upgrade-screen-cro)**: ---

### Pci Compliance
- **PCI Compliance (@pci-compliance)**: ---

### Pdf Official
- **Fillable fields (@fillable-fields)**: **CRITICAL: You MUST complete these steps in order. Do not skip ahead to writing code.**
- **PDF Processing Advanced Reference (@pdf-processing-advanced-reference)**: This document contains advanced PDF processing features, detailed examples, and additional libraries not covered in the main skill instructions.
- **PDF Processing Guide (@pdf-processing-guide)**: ---

### Pentest Checklist
- **Pentest Checklist (@pentest-checklist)**: ---

### Pentest Commands
- **Pentest Commands (@pentest-commands)**: ---

### Performance Optimizer
- **Performance Optimizer (@performance-optimizer)**: ---

### Performance Profiling
- **Performance Profiling (@performance-profiling)**: ---

### Performance Testing Review Multi Agent Review
- **Multi-Agent Code Review Orchestration Tool (@multi-agent-code-review-orchestration-tool)**: ---

### Personal Tool Builder
- **Personal Tool Builder (@personal-tool-builder)**: ---

### Phase Gated Debugging
- **Phase-Gated Debugging (@phase-gated-debugging)**: ---

### Pipecat Friday Agent
- **Pipecat Friday Agent (@pipecat-friday-agent)**: ---

### Pipedrive Automation
- **Pipedrive Automation via Rube MCP (@pipedrive-automation-via-rube-mcp)**: ---

### Plaid Fintech
- **Plaid Fintech (@plaid-fintech)**: ---

### Plan Writing
- **Plan Writing (@plan-writing)**: ---

### Planning With Files
- **Examples: Planning with Files in Action (@examples:-planning-with-files-in-action)**: **User Request:** "Research the benefits of morning exercise and write a summary"
- **Findings & Decisions (@findings-&-decisions)**: <!--
- **Planning with Files (@planning-with-files)**: ---
- **Progress Log (@progress-log)**: <!--
- **Reference: Manus Context Engineering Principles (@reference:-manus-context-engineering-principles)**: This skill is based on context engineering principles from Manus, the AI agent company acquired by Meta for $2 billion in December 2025.
- **Task Plan: [Brief Description] (@task-plan:-[brief-description])**: <!--

### Playwright Java
- **Playwright Java – Advanced Test Automation (@playwright-java-–-advanced-test-automation)**: ---
- **Playwright Java – Assertions Reference (@playwright-java-–-assertions-reference)**: ```java
- **Playwright Java – Fixtures, Hooks & Test Data (@playwright-java-–-fixtures,-hooks-&-test-data)**: Encapsulate browser lifecycle in a reusable JUnit 5 extension:
- **Playwright Java – Page Object Patterns (@playwright-java-–-page-object-patterns)**: For repeated UI components (navbars, modals, tables), create Component classes:
- **Playwright Java – Project Configuration (@playwright-java-–-project-configuration)**: ```xml

### Playwright Skill
- **Playwright Browser Automation (@playwright-browser-automation)**: ---
- **Playwright Skill - Complete API Reference (@playwright-skill---complete-api-reference)**: This document contains the comprehensive Playwright API reference and advanced patterns. For quick-start execution patterns, see [SKILL.md](SKILL.md).

### Plotly
- **Plotly (@plotly)**: ---

### Podcast Generation
- **Podcast Generation with GPT Realtime Mini (@podcast-generation-with-gpt-realtime-mini)**: ---

### Polars
- **Polars (@polars)**: ---

### Popup Cro
- **Popup CRO (@popup-cro)**: ---

### Postgres Best Practices
- **Postgres Best Practices (@postgres-best-practices)**: **Version 1.0.0**
- **Supabase Postgres Best Practices (@supabase-postgres-best-practices)**: ---
- **advanced-full-text-search.md (@advanced-full-text-search.md)**: ---
- **advanced-jsonb-indexing.md (@advanced-jsonb-indexing.md)**: ---
- **conn-limits.md (@conn-limits.md)**: ---
- **conn-pooling.md (@conn-pooling.md)**: ---
- **conn-prepared-statements.md (@conn-prepared-statements.md)**: ---
- **data-batch-inserts.md (@data-batch-inserts.md)**: ---
- **data-n-plus-one.md (@data-n-plus-one.md)**: ---
- **data-pagination.md (@data-pagination.md)**: ---
- **data-upsert.md (@data-upsert.md)**: ---
- **lock-advisory.md (@lock-advisory.md)**: ---
- **lock-deadlock-prevention.md (@lock-deadlock-prevention.md)**: ---
- **lock-short-transactions.md (@lock-short-transactions.md)**: ---
- **lock-skip-locked.md (@lock-skip-locked.md)**: ---
- **monitor-explain-analyze.md (@monitor-explain-analyze.md)**: ---
- **monitor-pg-stat-statements.md (@monitor-pg-stat-statements.md)**: ---
- **monitor-vacuum-analyze.md (@monitor-vacuum-analyze.md)**: ---
- **pgbouncer.ini (@pgbouncer.ini)**: ---
- **query-composite-indexes.md (@query-composite-indexes.md)**: ---
- **query-covering-indexes.md (@query-covering-indexes.md)**: ---
- **query-index-types.md (@query-index-types.md)**: ---
- **query-missing-indexes.md (@query-missing-indexes.md)**: ---
- **query-partial-indexes.md (@query-partial-indexes.md)**: ---
- **schema-data-types.md (@schema-data-types.md)**: ---
- **schema-foreign-key-indexes.md (@schema-foreign-key-indexes.md)**: ---
- **schema-lowercase-identifiers.md (@schema-lowercase-identifiers.md)**: ---
- **schema-partitioning.md (@schema-partitioning.md)**: ---
- **schema-primary-keys.md (@schema-primary-keys.md)**: ---
- **security-privileges.md (@security-privileges.md)**: ---
- **security-rls-basics.md (@security-rls-basics.md)**: ---
- **security-rls-performance.md (@security-rls-performance.md)**: ---

### Postgresql
- **PostgreSQL Table Design (@postgresql-table-design)**: ---

### Postgresql Optimization
- **PostgreSQL Optimization Workflow (@postgresql-optimization-workflow)**: ---

### Posthog Automation
- **PostHog Automation via Rube MCP (@posthog-automation-via-rube-mcp)**: ---

### Postmark Automation
- **Postmark Automation via Rube MCP (@postmark-automation-via-rube-mcp)**: ---

### Postmortem Writing
- **Postmortem Writing (@postmortem-writing)**: ---

### Powershell Windows
- **PowerShell Windows Patterns (@powershell-windows-patterns)**: ---

### Pptx Official
- **HTML to PowerPoint Guide (@html-to-powerpoint-guide)**: Convert HTML slides to PowerPoint presentations with accurate positioning using the `html2pptx.js` library.
- **Office Open XML Technical Reference for PowerPoint (@office-open-xml-technical-reference-for-powerpoint)**: **Important: Read this entire document before starting.** Critical XML schema rules and formatting requirements are covered throughout. Incorrect implementation can create invalid PPTX files that P...
- **PPTX creation, editing, and analysis (@pptx-creation,-editing,-and-analysis)**: ---

### Pr Writer
- **PR Writer (@pr-writer)**: ---

### Pricing Strategy
- **Pricing Strategy (@pricing-strategy)**: ---

### Prisma Expert
- **Prisma Expert (@prisma-expert)**: ---

### Privacy By Design
- **Privacy by Design (@privacy-by-design)**: ---

### Privilege Escalation Methods
- **Privilege Escalation Methods (@privilege-escalation-methods)**: ---

### Product Design
- **PRODUCT DESIGN — Nivel Apple (@product-design-—-nivel-apple)**: ---

### Product Inventor
- **PRODUCT INVENTOR — DESIGN ALCHEMIST v1.0 (@product-inventor-—-design-alchemist-v1.0)**: ---

### Product Manager
- **Product Manager Skills (@product-manager-skills)**: ---

### Product Manager Toolkit
- **Product Manager Toolkit (@product-manager-toolkit)**: ---
- **Product Requirements Document (PRD) Templates (@product-requirements-document-(prd)-templates)**: **Purpose**: One-page overview for executives and stakeholders

### Product Marketing Context
- **Product Marketing Context (@product-marketing-context)**: ---

### Production Code Audit
- **Production Code Audit (@production-code-audit)**: ---

### Production Scheduling
- **Communication Templates — Production Scheduling (@communication-templates-—-production-scheduling)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing production scheduling communications.
- **Decision Frameworks — Production Scheduling (@decision-frameworks-—-production-scheduling)**: This reference provides the detailed decision logic, scheduling algorithms, optimisation
- **Production Scheduling (@production-scheduling)**: ---
- **Production Scheduling — Edge Cases Reference (@production-scheduling-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous production scheduling situations that don't resolve through standard sequencing and dispatching workflows.

### Professional Proofreader
- **MODE 1: Inline Text (@mode-1:-inline-text)**: Extract only the text intended for proofreading.
- **Professional Proofreader (@professional-proofreader)**: ---
- **file-processing-mode.md (@file-processing-mode.md)**: Supported:

### Programmatic Seo
- **Programmatic SEO (@programmatic-seo)**: ---

### Progressive Estimation
- **Progressive Estimation (@progressive-estimation)**: ---

### Progressive Web App
- **Progressive Web Apps (PWAs) (@progressive-web-apps-(pwas))**: ---

### Project Development
- **Project Development Methodology (@project-development-methodology)**: ---

### Project Skill Audit
- **Project Skill Audit (@project-skill-audit)**: ---

### Projection Patterns
- **Projection Patterns (@projection-patterns)**: ---
- **Projection Patterns Implementation Playbook (@projection-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Prometheus Configuration
- **Prometheus Configuration (@prometheus-configuration)**: ---

### Prompt Caching
- **Prompt Caching (@prompt-caching)**: ---

### Prompt Engineering
- **Prompt Engineering Patterns (@prompt-engineering-patterns)**: ---

### Prompt Engineering Patterns
- **Chain-of-Thought Prompting (@chain-of-thought-prompting)**: Chain-of-Thought (CoT) prompting elicits step-by-step reasoning from LLMs, dramatically improving performance on complex reasoning, math, and logic tasks.
- **Few-Shot Learning Guide (@few-shot-learning-guide)**: Few-shot learning enables LLMs to perform tasks by providing a small number of examples (typically 1-10) within the prompt. This technique is highly effective for tasks requiring specific formats, ...
- **Prompt Optimization Guide (@prompt-optimization-guide)**: ```python
- **Prompt Template Library (@prompt-template-library)**: ```
- **Prompt Template Systems (@prompt-template-systems)**: ```python
- **System Prompt Design (@system-prompt-design)**: System prompts set the foundation for LLM behavior. They define role, expertise, constraints, and output expectations.

### Prompt Library
- **📝 Prompt Library (@📝-prompt-library)**: ---

### Protect Mcp Governance
- **MCP Agent Governance with protect-mcp (@mcp-agent-governance-with-protect-mcp)**: ---

### Protocol Reverse Engineering
- **Protocol Reverse Engineering (@protocol-reverse-engineering)**: ---
- **Protocol Reverse Engineering Implementation Playbook (@protocol-reverse-engineering-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Pubmed Database
- **PubMed Database (@pubmed-database)**: ---

### Pydantic Ai
- **PydanticAI — Typed AI Agents in Python (@pydanticai-—-typed-ai-agents-in-python)**: ---

### Pydantic Models Py
- **Pydantic Models (@pydantic-models)**: ---

### Pypict Skill
- **Pypict Skill (@pypict-skill)**: ---

### Python Development Python Scaffold
- **Python Project Scaffolding (@python-project-scaffolding)**: ---

### Python Fastapi Development
- **Python/FastAPI Development Workflow (@python/fastapi-development-workflow)**: ---

### Python Packaging
- **Python Packaging (@python-packaging)**: ---
- **Python Packaging Implementation Playbook (@python-packaging-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Python Patterns
- **Python Patterns (@python-patterns)**: ---

### Python Performance Optimization
- **Python Performance Optimization (@python-performance-optimization)**: ---
- **Python Performance Optimization Implementation Playbook (@python-performance-optimization-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Python Pptx Generator
- **Python PPTX Generator (@python-pptx-generator)**: ---

### Python Testing Patterns
- **Python Testing Patterns (@python-testing-patterns)**: ---
- **Python Testing Patterns Implementation Playbook (@python-testing-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Qiskit
- **Qiskit (@qiskit)**: ---

### Quality Nonconformance
- **Communication Templates — Quality & Non-Conformance Management (@communication-templates-—-quality-&-non-conformance-management)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing quality communications.
- **Decision Frameworks — Quality & Non-Conformance Management (@decision-frameworks-—-quality-&-non-conformance-management)**: This reference provides the detailed decision logic, MRB processes, RCA methodology selection,
- **Quality & Non-Conformance Management (@quality-&-non-conformance-management)**: ---
- **Quality & Non-Conformance Management — Edge Cases Reference (@quality-&-non-conformance-management-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous quality situations that don't resolve through standard NCR/CAPA workflows.

### Radix Ui Design System
- **Radix UI Design System (@radix-ui-design-system)**: ---

### Rag Engineer
- **RAG Engineer (@rag-engineer)**: ---

### Rag Implementation
- **RAG Implementation Workflow (@rag-implementation-workflow)**: ---

### React Best Practices
- **React Best Practices (@react-best-practices)**: **Version 0.1.0**
- **Vercel React Best Practices (@vercel-react-best-practices)**: ---
- **advanced-event-handler-refs.md (@advanced-event-handler-refs.md)**: ---
- **advanced-use-latest.md (@advanced-use-latest.md)**: ---
- **async-api-routes.md (@async-api-routes.md)**: ---
- **async-defer-await.md (@async-defer-await.md)**: ---
- **async-dependencies.md (@async-dependencies.md)**: ---
- **async-parallel.md (@async-parallel.md)**: ---
- **async-suspense-boundaries.md (@async-suspense-boundaries.md)**: ---
- **bundle-barrel-imports.md (@bundle-barrel-imports.md)**: ---
- **bundle-conditional.md (@bundle-conditional.md)**: ---
- **bundle-defer-third-party.md (@bundle-defer-third-party.md)**: ---
- **bundle-dynamic-imports.md (@bundle-dynamic-imports.md)**: ---
- **bundle-preload.md (@bundle-preload.md)**: ---
- **client-event-listeners.md (@client-event-listeners.md)**: ---
- **client-swr-dedup.md (@client-swr-dedup.md)**: ---
- **js-batch-dom-css.md (@js-batch-dom-css.md)**: ---
- **js-cache-function-results.md (@js-cache-function-results.md)**: ---
- **js-cache-property-access.md (@js-cache-property-access.md)**: ---
- **js-cache-storage.md (@js-cache-storage.md)**: ---
- **js-combine-iterations.md (@js-combine-iterations.md)**: ---
- **js-early-exit.md (@js-early-exit.md)**: ---
- **js-hoist-regexp.md (@js-hoist-regexp.md)**: ---
- **js-index-maps.md (@js-index-maps.md)**: ---
- **js-length-check-first.md (@js-length-check-first.md)**: ---
- **js-min-max-loop.md (@js-min-max-loop.md)**: ---
- **js-set-map-lookups.md (@js-set-map-lookups.md)**: ---
- **js-tosorted-immutable.md (@js-tosorted-immutable.md)**: ---
- **rendering-activity.md (@rendering-activity.md)**: ---
- **rendering-animate-svg-wrapper.md (@rendering-animate-svg-wrapper.md)**: ---
- **rendering-conditional-render.md (@rendering-conditional-render.md)**: ---
- **rendering-content-visibility.md (@rendering-content-visibility.md)**: ---
- **rendering-hoist-jsx.md (@rendering-hoist-jsx.md)**: ---
- **rendering-hydration-no-flicker.md (@rendering-hydration-no-flicker.md)**: ---
- **rendering-svg-precision.md (@rendering-svg-precision.md)**: ---
- **rerender-defer-reads.md (@rerender-defer-reads.md)**: ---
- **rerender-dependencies.md (@rerender-dependencies.md)**: ---
- **rerender-derived-state.md (@rerender-derived-state.md)**: ---
- **rerender-functional-setstate.md (@rerender-functional-setstate.md)**: ---
- **rerender-lazy-state-init.md (@rerender-lazy-state-init.md)**: ---
- **rerender-memo.md (@rerender-memo.md)**: ---
- **rerender-transitions.md (@rerender-transitions.md)**: ---
- **server-after-nonblocking.md (@server-after-nonblocking.md)**: ---
- **server-cache-lru.md (@server-cache-lru.md)**: ---
- **server-cache-react.md (@server-cache-react.md)**: ---
- **server-parallel-fetching.md (@server-parallel-fetching.md)**: ---
- **server-serialization.md (@server-serialization.md)**: ---

### React Component Performance
- **Examples (@examples)**: **Scenario:** A message list re-renders every second because a timer (`elapsedMs`) lives in the parent component. This causes visible jank on large lists.
- **React Component Performance (@react-component-performance)**: ---

### React Flow Architect
- **ReactFlow Architect (@reactflow-architect)**: ---

### React Flow Node Ts
- **React Flow Node (@react-flow-node)**: ---

### React Modernization
- **React Modernization (@react-modernization)**: ---
- **React Modernization Implementation Playbook (@react-modernization-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### React Native Architecture
- **React Native Architecture (@react-native-architecture)**: ---
- **React Native Architecture Implementation Playbook (@react-native-architecture-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### React Nextjs Development
- **React/Next.js Development Workflow (@react/next.js-development-workflow)**: ---

### React State Management
- **React State Management (@react-state-management)**: ---

### React Ui Patterns
- **React UI Patterns (@react-ui-patterns)**: ---

### Readme
- **README Generator (@readme-generator)**: ---

### Recallmax
- **RecallMax — God-Tier Long-Context Memory (@recallmax-—-god-tier-long-context-memory)**: ---

### Receiving Code Review
- **Code Review Reception (@code-review-reception)**: ---

### Red Team Tactics
- **Red Team Tactics (@red-team-tactics)**: ---

### Red Team Tools
- **Red Team Tools and Methodology (@red-team-tools-and-methodology)**: ---

### Reddit Automation
- **Reddit Automation via Rube MCP (@reddit-automation-via-rube-mcp)**: ---

### Referral Program
- **Referral & Affiliate Programs (@referral-&-affiliate-programs)**: ---

### Rehabilitation Analyzer
- **康复训练分析技能 (@康复训练分析技能)**: ---

### Remotion
- **Stitch to Remotion Walkthrough Videos (@stitch-to-remotion-walkthrough-videos)**: ---

### Remotion Best Practices
- **Charts in Remotion (@charts-in-remotion)**: ---
- **Checking if a video can be decoded (@checking-if-a-video-can-be-decoded)**: ---
- **Displaying captions in Remotion (@displaying-captions-in-remotion)**: ---
- **Extracting frames from videos (@extracting-frames-from-videos)**: ---
- **Getting audio duration with Mediabunny (@getting-audio-duration-with-mediabunny)**: ---
- **Getting video dimensions with Mediabunny (@getting-video-dimensions-with-mediabunny)**: ---
- **Getting video duration with Mediabunny (@getting-video-duration-with-mediabunny)**: ---
- **Importing .srt subtitles into Remotion (@importing-.srt-subtitles-into-remotion)**: ---
- **Importing assets in Remotion (@importing-assets-in-remotion)**: ---
- **Measuring DOM nodes in Remotion (@measuring-dom-nodes-in-remotion)**: ---
- **Measuring text in Remotion (@measuring-text-in-remotion)**: ---
- **Transcribing audio (@transcribing-audio)**: ---
- **Using Animated images in Remotion (@using-animated-images-in-remotion)**: ---
- **Using Lottie Animations in Remotion (@using-lottie-animations-in-remotion)**: ---
- **Using Three.js and React Three Fiber in Remotion (@using-three.js-and-react-three-fiber-in-remotion)**: ---
- **Using audio in Remotion (@using-audio-in-remotion)**: ---
- **Using calculateMetadata (@using-calculatemetadata)**: ---
- **Using fonts in Remotion (@using-fonts-in-remotion)**: ---
- **Using images in Remotion (@using-images-in-remotion)**: ---
- **Using videos in Remotion (@using-videos-in-remotion)**: ---
- **animations.md (@animations.md)**: ---
- **compositions.md (@compositions.md)**: ---
- **sequencing.md (@sequencing.md)**: ---
- **tailwind.md (@tailwind.md)**: ---
- **text-animations.md (@text-animations.md)**: ---
- **timing.md (@timing.md)**: ---
- **transitions.md (@transitions.md)**: ---
- **trimming.md (@trimming.md)**: ---

### Render Automation
- **Render Automation via Rube MCP (@render-automation-via-rube-mcp)**: ---

### Requesting Code Review
- **Code Review Agent (@code-review-agent)**: You are reviewing code changes for production readiness.
- **Requesting Code Review (@requesting-code-review)**: ---

### Returns Reverse Logistics
- **Communication Templates — Returns & Reverse Logistics (@communication-templates-—-returns-&-reverse-logistics)**: > **Reference Type:** Tier 3 — Load on demand when composing or reviewing returns-related communications.
- **Decision Frameworks — Returns & Reverse Logistics (@decision-frameworks-—-returns-&-reverse-logistics)**: This reference provides the detailed decision logic, scoring matrices, financial models,
- **Returns & Reverse Logistics (@returns-&-reverse-logistics)**: ---
- **Returns & Reverse Logistics — Edge Cases Reference (@returns-&-reverse-logistics-—-edge-cases-reference)**: > Tier 3 reference. Load on demand when handling complex or ambiguous return situations that don't resolve through standard workflows.

### Reverse Engineer
- **Common RE scripting environments (@common-re-scripting-environments)**: ---

### Revops
- **Automation Playbooks (@automation-playbooks)**: Platform-specific workflow recipes for HubSpot, Salesforce, scheduling tools, and cross-tool automation.
- **Lead Routing Rules (@lead-routing-rules)**: Decision trees, platform-specific configurations, territory routing, ABM routing, and speed-to-lead benchmarks.
- **Lead Scoring Models (@lead-scoring-models)**: Detailed scoring templates, example models by business type, and calibration guidance.
- **Lifecycle Stage Definitions (@lifecycle-stage-definitions)**: Complete templates for lead lifecycle stages, MQL criteria by business type, SLAs, and rejection/recycling workflows.
- **RevOps (@revops)**: ---

### Risk Metrics Calculation
- **Risk Metrics Calculation (@risk-metrics-calculation)**: ---
- **Risk Metrics Calculation Implementation Playbook (@risk-metrics-calculation-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Robius App Architecture
- **Robius App Architecture Skill (@robius-app-architecture-skill)**: ---

### Robius Event Action
- **Robius Event and Action Patterns Skill (@robius-event-and-action-patterns-skill)**: ---

### Robius Matrix Integration
- **Robius Matrix SDK Integration Skill (@robius-matrix-sdk-integration-skill)**: ---

### Robius State Management
- **Robius State Management Skill (@robius-state-management-skill)**: ---

### Robius Widget Patterns
- **Robius Widget Patterns Skill (@robius-widget-patterns-skill)**: ---

### Rust Async Patterns
- **Rust Async Patterns (@rust-async-patterns)**: ---
- **Rust Async Patterns Implementation Playbook (@rust-async-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Saas Multi Tenant
- **SaaS Multi-Tenant Architecture (@saas-multi-tenant-architecture)**: ---

### Saas Mvp Launcher
- **SaaS MVP Launcher (@saas-mvp-launcher)**: ---

### Saga Orchestration
- **Saga Orchestration (@saga-orchestration)**: ---
- **Saga Orchestration Playbook (@saga-orchestration-playbook)**: - Choose orchestration when business flow visibility and centralized control are required.

### Sales Enablement
- **Demo Script Templates (@demo-script-templates)**: Scene-by-scene templates for different call types, with timing, talk tracks, and interaction guidance.
- **Objection Library (@objection-library)**: Common B2B SaaS objections with response frameworks. Organized by category for quick reference.
- **One-Pager Templates (@one-pager-templates)**: Templates for different one-pager use cases, with layout guidance and copy prompts.
- **Sales Deck Frameworks (@sales-deck-frameworks)**: Detailed slide-by-slide guidance for building sales decks that tell a story and close deals.
- **Sales Enablement (@sales-enablement)**: ---

### Salesforce Automation
- **Salesforce Automation via Rube MCP (@salesforce-automation-via-rube-mcp)**: ---

### Salesforce Development
- **Salesforce Development (@salesforce-development)**: ---

### Sam Altman
- **SKILL: Sam Altman — Agente Persona v2 (@skill:-sam-altman-—-agente-persona-v2)**: ---

### Sankhya Dashboard Html Jsp Custom Best Pratices
- **sankhya-dashboard-html-jsp-custom-best-pratices (@sankhya-dashboard-html-jsp-custom-best-pratices)**: ---

### Sast Configuration
- **SAST Configuration (@sast-configuration)**: ---

### Satori
- **Satori (@satori)**: ---

### Scanning Tools
- **Security Scanning Tools (@security-scanning-tools)**: ---

### Scanpy
- **Scanpy: Single-Cell Analysis (@scanpy:-single-cell-analysis)**: ---

### Schema Markup
- **Schema Markup & Structured Data (@schema-markup-&-structured-data)**: ---

### Scientific Writing
- **Scientific Writing (@scientific-writing)**: ---

### Scikit Learn
- **Scikit-learn (@scikit-learn)**: ---

### Screen Reader Testing
- **Screen Reader Testing (@screen-reader-testing)**: ---
- **Screen Reader Testing Implementation Playbook (@screen-reader-testing-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Screenshots
- **Screenshots (@screenshots)**: ---

### Scroll Experience
- **Scroll Experience (@scroll-experience)**: ---

### Seaborn
- **Seaborn Statistical Visualization (@seaborn-statistical-visualization)**: ---

### Secrets Management
- **Secrets Management (@secrets-management)**: ---

### Security
- **AWS Compliance Checker (@aws-compliance-checker)**: ---
- **AWS IAM Best Practices (@aws-iam-best-practices)**: ---
- **AWS Secrets Rotation (@aws-secrets-rotation)**: ---
- **AWS Security Audit (@aws-security-audit)**: ---

### Security Audit
- **Security Auditing Workflow Bundle (@security-auditing-workflow-bundle)**: ---

### Security Bluebook Builder
- **Security Bluebook Builder (@security-bluebook-builder)**: ---

### Security Compliance Compliance Check
- **Regulatory Compliance Check (@regulatory-compliance-check)**: ---
- **Regulatory Compliance Check Implementation Playbook (@regulatory-compliance-check-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Security Requirement Extraction
- **Security Requirement Extraction (@security-requirement-extraction)**: ---
- **Security Requirement Extraction Implementation Playbook (@security-requirement-extraction-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Security Scanning Security Dependencies
- **Dependency Vulnerability Scanning (@dependency-vulnerability-scanning)**: ---
- **Dependency Vulnerability Scanning Implementation Playbook (@dependency-vulnerability-scanning-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Security Scanning Security Sast
- **SAST Security Plugin (@sast-security-plugin)**: ---

### Seek And Analyze Video
- **Seek and Analyze Video (@seek-and-analyze-video)**: ---

### Segment Automation
- **Segment Automation via Rube MCP (@segment-automation-via-rube-mcp)**: ---

### Segment Cdp
- **Segment CDP (@segment-cdp)**: ---

### Semgrep Rule Creator
- **Semgrep Rule Creator (@semgrep-rule-creator)**: ---

### Semgrep Rule Variant Creator
- **Semgrep Rule Variant Creator (@semgrep-rule-variant-creator)**: ---

### Sendgrid Automation
- **SendGrid Automation via Rube MCP (@sendgrid-automation-via-rube-mcp)**: ---

### Senior Architect
- **Senior Architect (@senior-architect)**: ---
- **System Design Workflows (@system-design-workflows)**: This reference guide provides comprehensive information for senior architect.
- **Tech Decision Guide (@tech-decision-guide)**: This reference guide provides comprehensive information for senior architect.

### Senior Frontend
- **Frontend Best Practices (@frontend-best-practices)**: Modern frontend development standards for accessibility, testing, TypeScript, and Tailwind CSS.
- **Next.js Optimization Guide (@next.js-optimization-guide)**: Performance optimization techniques for Next.js 14+ applications.
- **React Patterns (@react-patterns)**: Production-ready patterns for building scalable React applications with TypeScript.
- **Senior Frontend (@senior-frontend)**: ---

### Senior Fullstack
- **Architecture Patterns (@architecture-patterns)**: This reference guide provides comprehensive information for senior fullstack.
- **Development Workflows (@development-workflows)**: This reference guide provides comprehensive information for senior fullstack.
- **Senior Fullstack (@senior-fullstack)**: ---
- **Tech Stack Guide (@tech-stack-guide)**: This reference guide provides comprehensive information for senior fullstack.

### Sentry Automation
- **Sentry Automation via Rube MCP (@sentry-automation-via-rube-mcp)**: ---

### Seo
- **Content Quality Gates (@content-quality-gates)**: | Page Type | Min Words | Unique Content % | Notes |
- **Core Web Vitals Thresholds (February 2026) (@core-web-vitals-thresholds-(february-2026))**: <!-- Updated: 2026-02-07 -->
- **E-E-A-T Evaluation Framework (@e-e-a-t-evaluation-framework)**: E-E-A-T = **E**xperience, **E**xpertise, **A**uthoritativeness, **T**rustworthiness
- **SEO: Universal SEO Analysis Skill (@seo:-universal-seo-analysis-skill)**: ---
- **Schema.org Types: Status & Recommendations (February 2026) (@schema.org-types:-status-&-recommendations-(february-2026))**: <!-- Updated: 2026-02-07 -->

### Seo Aeo Blog Writer
- **SEO-AEO Blog Writer (@seo-aeo-blog-writer)**: ---

### Seo Aeo Content Cluster
- **SEO-AEO Content Cluster (@seo-aeo-content-cluster)**: ---

### Seo Aeo Content Quality Auditor
- **SEO-AEO Content Quality Auditor (@seo-aeo-content-quality-auditor)**: ---

### Seo Aeo Internal Linking
- **SEO-AEO Internal Linking (@seo-aeo-internal-linking)**: ---

### Seo Aeo Keyword Research
- **SEO-AEO Keyword Research (@seo-aeo-keyword-research)**: ---

### Seo Aeo Landing Page Writer
- **SEO-AEO Landing Page Writer (@seo-aeo-landing-page-writer)**: ---

### Seo Aeo Meta Description Generator
- **SEO-AEO Meta Description Generator (@seo-aeo-meta-description-generator)**: ---

### Seo Aeo Schema Generator
- **SEO-AEO Schema Generator (@seo-aeo-schema-generator)**: ---

### Seo Audit
- **SEO Audit (@seo-audit)**: ---

### Seo Competitor Pages
- **Competitor Comparison & Alternatives Pages (@competitor-comparison-&-alternatives-pages)**: ---

### Seo Content
- **Content Quality & E-E-A-T Analysis (@content-quality-&-e-e-a-t-analysis)**: ---

### Seo Dataforseo
- **DataForSEO: Live SEO Data (Extension) (@dataforseo:-live-seo-data-(extension))**: ---

### Seo Forensic Incident Response
- **SEO Forensic Incident Response (@seo-forensic-incident-response)**: ---

### Seo Fundamentals
- **SEO Fundamentals (@seo-fundamentals)**: ---

### Seo Geo
- **AI Search / GEO Optimization (February 2026) (@ai-search-/-geo-optimization-(february-2026))**: ---

### Seo Hreflang
- **Hreflang & International SEO (@hreflang-&-international-seo)**: ---

### Seo Image Gen
- **SEO Image Gen: AI Image Generation for SEO Assets (Extension) (@seo-image-gen:-ai-image-generation-for-seo-assets-(extension))**: ---

### Seo Images
- **Image Optimization Analysis (@image-optimization-analysis)**: ---

### Seo Page
- **Single Page Analysis (@single-page-analysis)**: ---

### Seo Plan
- **Agency/Consultancy SEO Strategy Template (@agency/consultancy-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **E-commerce SEO Strategy Template (@e-commerce-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **Generic Business SEO Strategy Template (@generic-business-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **Local Service Business SEO Strategy Template (@local-service-business-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **Publisher/Media SEO Strategy Template (@publisher/media-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **SaaS SEO Strategy Template (@saas-seo-strategy-template)**: <!-- Updated: 2026-02-07 -->
- **Strategic SEO Planning (@strategic-seo-planning)**: ---

### Seo Programmatic
- **Programmatic SEO Analysis & Planning (@programmatic-seo-analysis-&-planning)**: ---

### Seo Schema
- **Schema Markup Analysis & Generation (@schema-markup-analysis-&-generation)**: ---

### Seo Sitemap
- **Sitemap Analysis & Generation (@sitemap-analysis-&-generation)**: ---

### Seo Technical
- **Technical SEO Audit (@technical-seo-audit)**: ---

### Server Management
- **Server Management (@server-management)**: ---

### Service Mesh Expert
- **Service Mesh Expert (@service-mesh-expert)**: ---

### Service Mesh Observability
- **Service Mesh Observability (@service-mesh-observability)**: ---

### Sexual Health Analyzer
- **性健康分析技能 (@性健康分析技能)**: ---

### Shadcn
- **Base vs Radix (@base-vs-radix)**: API differences between `base` and `radix`. Check the `base` field from `npx shadcn@latest info`.
- **Component Composition (@component-composition)**: - Items always inside their Group component
- **Customization & Theming (@customization-&-theming)**: Components reference semantic CSS variable tokens. Change the variables to change every component.
- **Forms & Inputs (@forms-&-inputs)**: - Forms use FieldGroup + Field
- **Styling & Customization (@styling-&-customization)**: See [customization.md](../customization.md) for theming, CSS variables, and adding custom colors.
- **shadcn CLI Reference (@shadcn-cli-reference)**: Configuration is read from `components.json`.
- **shadcn MCP Server (@shadcn-mcp-server)**: The CLI includes an MCP server that lets AI assistants search, browse, view, and install components from registries.
- **shadcn/ui (@shadcn/ui)**: ---

### Shader Programming Glsl
- **Shader Programming GLSL (@shader-programming-glsl)**: ---

### Sharp Edges
- **Sharp Edges Analysis (@sharp-edges-analysis)**: ---

### Shellcheck Configuration
- **ShellCheck Configuration and Static Analysis (@shellcheck-configuration-and-static-analysis)**: ---

### Shodan Reconnaissance
- **Shodan Reconnaissance and Pentesting (@shodan-reconnaissance-and-pentesting)**: ---

### Shopify Apps
- **Shopify Apps (@shopify-apps)**: ---

### Shopify Automation
- **Shopify Automation via Rube MCP (@shopify-automation-via-rube-mcp)**: ---

### Shopify Development
- **App Development Reference (@app-development-reference)**: Guide for building Shopify apps with OAuth, GraphQL/REST APIs, webhooks, and billing.
- **Extensions Reference (@extensions-reference)**: Guide for building UI extensions and Shopify Functions.
- **Shopify Development Skill (@shopify-development-skill)**: ---
- **Themes Reference (@themes-reference)**: Guide for developing Shopify themes with Liquid templating.

### Signup Flow Cro
- **Signup Flow CRO (@signup-flow-cro)**: ---

### Similarity Search Patterns
- **Similarity Search Patterns (@similarity-search-patterns)**: ---
- **Similarity Search Patterns Implementation Playbook (@similarity-search-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Simplify Code
- **Simplify Code (@simplify-code)**: ---

### Site Architecture
- **Mermaid Diagram Templates (@mermaid-diagram-templates)**: Copy-paste-ready Mermaid diagrams for visual sitemaps. Customize node labels and connections for your site.
- **Navigation Patterns (@navigation-patterns)**: Detailed navigation patterns for different site types and contexts.
- **Site Architecture (@site-architecture)**: ---
- **Site Type Templates (@site-type-templates)**: Full page hierarchy templates with ASCII trees, URL maps, and navigation recommendations for common site types.

### Skill Check
- **SkillCheck (@skillcheck)**: ---

### Skill Creator
- **Output Patterns (@output-patterns)**: Use these patterns when skills need to produce consistent, high-quality output.

### Skill Creator Ms
- **Skill Creator (@skill-creator)**: ---

### Skill Developer
- **Advanced Topics & Future Enhancements (@advanced-topics-&-future-enhancements)**: Ideas and concepts for future improvements to the skill system.
- **Common Patterns Library (@common-patterns-library)**: Ready-to-use regex and glob patterns for skill triggers. Copy and customize for your skills.
- **Hook Mechanisms - Deep Dive (@hook-mechanisms---deep-dive)**: Technical deep dive into how the UserPromptSubmit and PreToolUse hooks work.
- **Skill Developer Guide (@skill-developer-guide)**: ---
- **Trigger Types - Complete Guide (@trigger-types---complete-guide)**: Complete reference for configuring skill triggers in Claude Code's skill auto-activation system.
- **Troubleshooting - Skill Activation Issues (@troubleshooting---skill-activation-issues)**: Complete debugging guide for skill activation problems.
- **skill-rules.json - Complete Reference (@skill-rules.json---complete-reference)**: Complete schema and configuration reference for `.claude/skills/skill-rules.json`.

### Skill Improver
- **Skill Improvement Methodology (@skill-improvement-methodology)**: ---

### Skill Installer
- **Locais Conhecidos para Deteccao de Skills (@locais-conhecidos-para-deteccao-de-skills)**: O `detect_skills.py` escaneia os seguintes locais para encontrar skills nao-instaladas:
- **Skill Installer v3.0 (@skill-installer-v3.0)**: ---

### Skill Rails Upgrade
- **Rails Upgrade Analyzer (@rails-upgrade-analyzer)**: ---

### Skill Router
- **Skill Router (@skill-router)**: ---

### Skill Scanner
- **Skill Security Scanner (@skill-security-scanner)**: ---

### Skill Seekers
- **Skill Seekers (@skill-seekers)**: ---

### Skill Sentinel
- **Criterios de Analise - Skill Sentinel (@criterios-de-analise---skill-sentinel)**: Cada dimensao inicia com score 100 e sofre deducoes por violacoes encontradas.
- **Padroes de Seguranca (@padroes-de-seguranca)**: ```python
- **Schema do Banco de Dados - Sentinel (@schema-do-banco-de-dados---sentinel)**: Banco: `data/sentinel.db` (SQLite, WAL mode)
- **Skill Sentinel (@skill-sentinel)**: ---
- **Template para Novas Skills (@template-para-novas-skills)**: Use este template ao criar skills recomendadas pelo Sentinel.

### Skill Writer
- **Skill Writer (@skill-writer)**: ---

### Skin Health Analyzer
- **皮肤健康分析技能 (@皮肤健康分析技能)**: ---

### Slack Automation
- **Slack Automation via Rube MCP (@slack-automation-via-rube-mcp)**: ---

### Slack Bot Builder
- **Slack Bot Builder (@slack-bot-builder)**: ---

### Slack Gif Creator
- **Slack GIF Creator (@slack-gif-creator)**: ---

### Sleep Analyzer
- **睡眠分析器技能 (@睡眠分析器技能)**: ---

### Slo Implementation
- **SLO Implementation (@slo-implementation)**: ---

### Smtp Penetration Testing
- **SMTP Penetration Testing (@smtp-penetration-testing)**: ---

### Snowflake Development
- **Snowflake Development (@snowflake-development)**: ---

### Social Content
- **Social Content (@social-content)**: ---

### Social Orchestrator
- **SOCIAL-ORCHESTRATOR: Canais Unificados (@social-orchestrator:-canais-unificados)**: ---

### Software Architecture
- **Software Architecture Development Skill (@software-architecture-development-skill)**: ---

### Solidity Security
- **Solidity Security (@solidity-security)**: ---
- **Solidity Security Implementation Playbook (@solidity-security-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Spark Optimization
- **Apache Spark Optimization (@apache-spark-optimization)**: ---

### Spdd
- **ROLE: Codebase Research Agent (@role:-codebase-research-agent)**: Sua única missão é documentar e explicar a base de código como ela existe hoje.
- **ROLE: Implementation Execution Agent (@role:-implementation-execution-agent)**: Você deve implementar um plano técnico aprovado com precisão cirúrgica.
- **ROLE: Implementation Planning Agent (@role:-implementation-planning-agent)**: Você deve criar planos de implementação detalhados e ser cético quanto a requisitos vagos.

### Spec To Code Compliance
- **Spec-to-Code Compliance Checker Skill (@spec-to-code-compliance-checker-skill)**: ---

### Speckit Updater
- **SpecKit Safe Update (@speckit-safe-update)**: ---

### Speed
- **Speed Reader (@speed-reader)**: ---

### Spline 3D Integration
- **Common Problems & Debugging (@common-problems-&-debugging)**: These are the real-world issues that only surface after integration. Read this before finishing any Spline implementation.
- **Performance & Mobile Optimization (@performance-&-mobile-optimization)**: Spline scenes are WebGL — they run on the GPU. A poorly optimized scene will tank your PageSpeed score, lag on mid-range devices, and drain mobile batteries. Treat them like video files, not images.
- **React / Next.js / Vue Integration (@react-/-next.js-/-vue-integration)**: ---
- **Spline 3D Integration Skill (@spline-3d-integration-skill)**: ---
- **Vanilla JS / HTML Integration (@vanilla-js-/-html-integration)**: Two methods depending on how much control you need.

### Sql Injection Testing
- **SQL Injection Testing (@sql-injection-testing)**: ---

### Sql Optimization Patterns
- **SQL Optimization Patterns (@sql-optimization-patterns)**: ---
- **SQL Optimization Patterns Implementation Playbook (@sql-optimization-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Sqlmap Database Pentesting
- **SQLMap Database Penetration Testing (@sqlmap-database-penetration-testing)**: ---

### Square Automation
- **Square Automation via Rube MCP (@square-automation-via-rube-mcp)**: ---

### Sred Project Organizer
- **SRED Project Organization (@sred-project-organization)**: ---

### Sred Work Summary
- **SRED Work Summary (@sred-work-summary)**: ---

### Ssh Penetration Testing
- **SSH Penetration Testing (@ssh-penetration-testing)**: ---

### Stability Ai
- **API Reference — Stability AI v2beta (@api-reference-—-stability-ai-v2beta)**: 1. [Autenticacao](#autenticacao)
- **Prompt Engineering para Stable Diffusion (@prompt-engineering-para-stable-diffusion)**: 1. [Estrutura do Prompt](#estrutura-do-prompt)
- **Setup Guide — Stable Diffusion Skill (@setup-guide-—-stable-diffusion-skill)**: 1. Acesse **https://platform.stability.ai**
- **Stability AI — Gerador de Imagens Profissional (@stability-ai-—-gerador-de-imagens-profissional)**: ---

### Startup Business Analyst Business Case
- **Business Case Generator (@business-case-generator)**: ---

### Startup Business Analyst Financial Projections
- **Financial Projections (@financial-projections)**: ---

### Startup Business Analyst Market Opportunity
- **Market Opportunity Analysis (@market-opportunity-analysis)**: ---

### Startup Financial Modeling
- **Startup Financial Modeling (@startup-financial-modeling)**: ---

### Startup Metrics Framework
- **Startup Metrics Framework (@startup-metrics-framework)**: ---
- **Startup Metrics Framework Implementation Playbook (@startup-metrics-framework-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Statsmodels
- **Statsmodels: Statistical Modeling and Econometrics (@statsmodels:-statistical-modeling-and-econometrics)**: ---

### Steve Jobs
- **STEVE JOBS — AGENTE DE SIMULACAO PROFUNDA v2.0 (@steve-jobs-—-agente-de-simulacao-profunda-v2.0)**: ---

### Stitch Loop
- **Stitch Build Loop (@stitch-build-loop)**: ---

### Stitch Ui Design
- **Advanced Stitch Techniques (@advanced-stitch-techniques)**: Advanced strategies for maximizing Stitch's capabilities and creating production-ready designs.
- **Stitch Prompt Examples Library (@stitch-prompt-examples-library)**: Comprehensive collection of effective Stitch prompts organized by use case and complexity level.
- **Stitch UI Design Prompting (@stitch-ui-design-prompting)**: ---

### Stride Analysis Patterns
- **STRIDE Analysis Patterns (@stride-analysis-patterns)**: ---
- **STRIDE Analysis Patterns Implementation Playbook (@stride-analysis-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Stripe Automation
- **Stripe Automation via Rube MCP (@stripe-automation-via-rube-mcp)**: ---

### Stripe Integration
- **Stripe Integration (@stripe-integration)**: ---

### Subagent Driven Development
- **Code Quality Reviewer Prompt Template (@code-quality-reviewer-prompt-template)**: Use this template when dispatching a code quality reviewer subagent.
- **Implementer Subagent Prompt Template (@implementer-subagent-prompt-template)**: Use this template when dispatching an implementer subagent.
- **Spec Compliance Reviewer Prompt Template (@spec-compliance-reviewer-prompt-template)**: Use this template when dispatching a spec compliance reviewer subagent.
- **Subagent-Driven Development (@subagent-driven-development)**: ---

### Supabase Automation
- **Supabase Automation via Rube MCP (@supabase-automation-via-rube-mcp)**: ---

### Superpowers Lab
- **Superpowers Lab (@superpowers-lab)**: ---

### Supply Chain Risk Auditor
- **Supply Chain Risk Auditor (@supply-chain-risk-auditor)**: ---

### Sveltekit
- **SvelteKit Full-Stack Development (@sveltekit-full-stack-development)**: ---

### Swift Concurrency Expert
- **Swift Concurrency Expert (@swift-concurrency-expert)**: ---
- **SwiftUI Concurrency Tour (Summary) (@swiftui-concurrency-tour-(summary))**: Context: SwiftUI-focused concurrency overview covering actor isolation, Sendable closures, and how SwiftUI runs work off the main thread.
- **approachable-concurrency.md (@approachable-concurrency.md)**: Use this reference when the project has opted into the Swift 6.2 approachable
- **swift-6-2-concurrency.md (@swift-6-2-concurrency.md)**: Concurrent programming is hard because sharing memory between multiple tasks is prone to mistakes that lead to unpredictable behavior.

### Swiftui Expert Skill
- **SwiftUI Expert Skill (@swiftui-expert-skill)**: ---

### Swiftui Liquid Glass
- **Implementing Liquid Glass Design in SwiftUI (@implementing-liquid-glass-design-in-swiftui)**: Liquid Glass is a dynamic material introduced in iOS that combines the optical properties of glass with a sense of fluidity. It blurs content behind it, reflects color and light from surrounding co...
- **SwiftUI Liquid Glass (@swiftui-liquid-glass)**: ---

### Swiftui Performance Audit
- **Audit output template (@audit-output-template)**: Use this structure when reporting SwiftUI performance findings so the user can quickly see the symptom, evidence, likely cause, and next validation step.
- **Common code smells and remediation patterns (@common-code-smells-and-remediation-patterns)**: Use this reference during code-first review to map visible SwiftUI patterns to likely runtime costs and safer remediation guidance.
- **Demystify SwiftUI Performance (WWDC23) (Summary) (@demystify-swiftui-performance-(wwdc23)-(summary))**: Context: WWDC23 session on building a mental model for SwiftUI performance and triaging hangs/hitches.
- **Optimizing SwiftUI Performance with Instruments (Summary) (@optimizing-swiftui-performance-with-instruments-(summary))**: Context: WWDC session introducing the next-generation SwiftUI Instrument in Instruments 26 and how to diagnose SwiftUI-specific bottlenecks.
- **Profiling intake and collection checklist (@profiling-intake-and-collection-checklist)**: Use this checklist when code review alone cannot explain the SwiftUI performance issue and you need runtime evidence from the user.
- **SwiftUI Performance Audit (@swiftui-performance-audit)**: ---
- **Understanding Hangs in Your App (Summary) (@understanding-hangs-in-your-app-(summary))**: Context: Apple guidance on identifying hangs caused by long-running main-thread work and understanding the main run loop.
- **Understanding and Improving SwiftUI Performance (Summary) (@understanding-and-improving-swiftui-performance-(summary))**: Context: Apple guidance on diagnosing SwiftUI performance with Instruments and applying design patterns to reduce long or frequent updates.

### Swiftui Ui Patterns
- **App wiring and dependency graph (@app-wiring-and-dependency-graph)**: Show how to wire the app shell (TabView + NavigationStack + sheets) and install a global dependency graph (environment objects, services, streaming clients, SwiftData ModelContainer) in one place.
- **Async state and task lifecycle (@async-state-and-task-lifecycle)**: Use this pattern when a view loads data, reacts to changing input, or coordinates async work that should follow the SwiftUI view lifecycle.
- **Components Index (@components-index)**: Use this file to find component and cross-cutting guidance. Each entry lists when to use it.
- **Controls (Toggle, Slider, Picker) (@controls-(toggle,-slider,-picker))**: Use native controls for settings and configuration screens, keeping labels accessible and state bindings clear.
- **Deep links and navigation (@deep-links-and-navigation)**: Route external URLs into in-app destinations while falling back to system handling when needed.
- **Focus handling and field chaining (@focus-handling-and-field-chaining)**: Use `@FocusState` to control keyboard focus, chain fields, and coordinate focus across complex forms.
- **Form (@form)**: Use `Form` for structured settings, grouped inputs, and action rows. This pattern keeps layout, spacing, and accessibility consistent for data entry screens.
- **Grids (@grids)**: Use `LazyVGrid` for icon pickers, media galleries, and dense visual selections where items align in columns.
- **Haptics (@haptics)**: Use haptics sparingly to reinforce user actions (tab selection, refresh, success/error) and respect user preferences.
- **Input toolbar (bottom anchored) (@input-toolbar-(bottom-anchored))**: Use a bottom-anchored input bar for chat, composer, or quick actions without fighting the keyboard.
- **Lightweight Clients (Closure-Based) (@lightweight-clients-(closure-based))**: Use this pattern to keep networking or service dependencies simple and testable without introducing a full view model or heavy DI framework. It works well for SwiftUI apps where you want a small, c...
- **List and Section (@list-and-section)**: Use `List` for feed-style content and settings-style rows where built-in row reuse, selection, and accessibility matter.
- **Loading & Placeholders (@loading-&-placeholders)**: Use this when a view needs a consistent loading state (skeletons, redaction, empty state) without blocking interaction.
- **Matched transitions (@matched-transitions)**: Use matched transitions to create smooth continuity between a source view (thumbnail, avatar) and a destination view (sheet, detail, viewer).
- **Media (images, video, viewer) (@media-(images,-video,-viewer))**: Use consistent patterns for loading images, previewing media, and presenting a full-screen viewer.
- **Menu Bar (@menu-bar)**: Use this when adding or customizing the macOS/iPadOS menu bar with SwiftUI commands.
- **NavigationStack (@navigationstack)**: Use this pattern for programmatic navigation and deep links, especially when each tab needs an independent navigation history. The key idea is one `NavigationStack` per tab, each with its own path ...
- **Overlay and toasts (@overlay-and-toasts)**: Use overlays for transient UI (toasts, banners, loaders) without affecting layout.
- **Performance guardrails (@performance-guardrails)**: Use these rules when a SwiftUI screen is large, scroll-heavy, frequently updated, or at risk of unnecessary recomputation.
- **Previews (@previews)**: Use previews to validate layout, state wiring, and injected dependencies without relying on a running app or live services.
- **Scroll-reveal detail surfaces (@scroll-reveal-detail-surfaces)**: Use this pattern when a detail screen has a primary surface first and secondary content behind it, and you want the user to reveal that secondary layer by scrolling or swiping instead of tapping a ...
- **ScrollView and Lazy stacks (@scrollview-and-lazy-stacks)**: Use `ScrollView` with `LazyVStack`, `LazyHStack`, or `LazyVGrid` when you need custom layout, mixed content, or horizontal/ grid-based scrolling.
- **Searchable (@searchable)**: Use `searchable` to add native search UI with optional scopes and async results.
- **Sheets (@sheets)**: Use a centralized sheet routing pattern so any view can present modals without prop-drilling. This keeps sheet state in one place and scales as the app grows.
- **Split views and columns (@split-views-and-columns)**: Provide a lightweight, customizable multi-column layout for iPad/macOS without relying on `NavigationSplitView`.
- **SwiftUI UI Patterns (@swiftui-ui-patterns)**: ---
- **TabView (@tabview)**: Use this pattern for a scalable, multi-platform tab architecture with:
- **Theming and dynamic type (@theming-and-dynamic-type)**: Provide a clean, scalable theming approach that keeps view code semantic and consistent.
- **Title menus (@title-menus)**: Use a title menu in the navigation bar to provide context‑specific filtering or quick actions without adding extra chrome.
- **Top bar overlays (iOS 26+ and fallback) (@top-bar-overlays-(ios-26+-and-fallback))**: Provide a custom top selector or pill row that sits above scroll content, using `safeAreaBar(.top)` on iOS 26 and a compatible fallback on earlier OS versions.
- **macOS Settings (@macos-settings)**: Use this when building a macOS Settings window backed by SwiftUI's `Settings` scene.

### Swiftui View Refactor
- **MV Patterns Reference (@mv-patterns-reference)**: Distilled guidance for deciding whether a SwiftUI feature should stay as plain MV or introduce a view model.
- **SwiftUI View Refactor (@swiftui-view-refactor)**: ---

### Sympy
- **SymPy - Symbolic Mathematics in Python (@sympy---symbolic-mathematics-in-python)**: ---

### Systematic Debugging
- **Academic Test: Systematic Debugging Skill (@academic-test:-systematic-debugging-skill)**: You have access to the systematic debugging skill at skills/debugging/systematic-debugging
- **Condition-Based Waiting (@condition-based-waiting)**: Flaky tests often guess at timing with arbitrary delays. This creates race conditions where tests pass on fast machines but fail under load or in CI.
- **Creation Log: Systematic Debugging Skill (@creation-log:-systematic-debugging-skill)**: Reference example of extracting, structuring, and bulletproofing a critical skill.
- **Defense-in-Depth Validation (@defense-in-depth-validation)**: When you fix a bug caused by invalid data, adding validation at one place feels sufficient. But that single check can be bypassed by different code paths, refactoring, or mocks.
- **Pressure Test 1: Emergency Production Fix (@pressure-test-1:-emergency-production-fix)**: **IMPORTANT: This is a real scenario. You must choose and act. Don't ask hypothetical questions - make the actual decision.**
- **Pressure Test 2: Sunk Cost + Exhaustion (@pressure-test-2:-sunk-cost-+-exhaustion)**: **IMPORTANT: This is a real scenario. You must choose and act. Don't ask hypothetical questions - make the actual decision.**
- **Pressure Test 3: Authority + Social Pressure (@pressure-test-3:-authority-+-social-pressure)**: **IMPORTANT: This is a real scenario. You must choose and act. Don't ask hypothetical questions - make the actual decision.**
- **Root Cause Tracing (@root-cause-tracing)**: Bugs often manifest deep in the call stack (git init in wrong directory, file created in wrong location, database opened with wrong path). Your instinct is to fix where the error appears, but that'...
- **Systematic Debugging (@systematic-debugging)**: ---

### Systems Programming Rust Project
- **Rust Project Scaffolding (@rust-project-scaffolding)**: ---

### Tailwind Design System
- **Tailwind Design System (@tailwind-design-system)**: ---
- **Tailwind Design System Implementation Playbook (@tailwind-design-system-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Tailwind Patterns
- **Tailwind CSS Patterns (v4 - 2025) (@tailwind-css-patterns-(v4---2025))**: ---

### Tanstack Query Expert
- **TanStack Query Expert (@tanstack-query-expert)**: ---

### Task Intelligence
- **Catálogo de Problemas por Domínio (@catálogo-de-problemas-por-domínio)**: | Problema | Frequência | Solução Preventiva |
- **Padrões Históricos de Tempo por Tipo de Tarefa (@padrões-históricos-de-tempo-por-tipo-de-tarefa)**: Baseado em execuções reais do ecossistema.
- **Task Intelligence — Protocolo de Amplificação Pré-Tarefa (@task-intelligence-—-protocolo-de-amplificação-pré-tarefa)**: ---

### Tavily Web
- **tavily-web (@tavily-web)**: ---

### Tcm Constitution Analyzer
- **中医体质辨识分析器技能 (@中医体质辨识分析器技能)**: ---

### Tdd Workflow
- **TDD Workflow (@tdd-workflow)**: ---

### Tdd Workflows Tdd Green
- **Green Phase: Simple function (@green-phase:-simple-function)**: ---
- **Green Phase: Simple function Implementation Playbook (@green-phase:-simple-function-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Team Collaboration Issue
- **GitHub Issue Resolution Expert (@github-issue-resolution-expert)**: ---
- **GitHub Issue Resolution Expert Implementation Playbook (@github-issue-resolution-expert-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Team Collaboration Standup Notes
- **Standup Notes Generator (@standup-notes-generator)**: ---
- **Standup Notes Generator Implementation Playbook (@standup-notes-generator-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Team Composition Analysis
- **Team Composition Analysis (@team-composition-analysis)**: ---

### Technical Change Tracker
- **Technical Change Tracker (@technical-change-tracker)**: ---

### Telegram
- **Gerenciamento de Chats - Telegram Bot (@gerenciamento-de-chats---telegram-bot)**: 1. [Tipos de Chat](#tipos-de-chat)
- **Recursos Avancados - Telegram Bot (@recursos-avancados---telegram-bot)**: 1. [Inline Mode](#inline-mode)
- **Telegram Bot API - Integracao Profissional (@telegram-bot-api---integracao-profissional)**: ---
- **Telegram Bot API - Referencia Completa (@telegram-bot-api---referencia-completa)**: 1. [Autenticacao](#autenticacao)
- **Webhook Setup - Telegram Bot (@webhook-setup---telegram-bot)**: 1. [Conceitos](#conceitos)

### Telegram Automation
- **Telegram Automation via Rube MCP (@telegram-automation-via-rube-mcp)**: ---

### Telegram Bot Builder
- **Telegram Bot Builder (@telegram-bot-builder)**: ---

### Telegram Mini App
- **Telegram Mini App (@telegram-mini-app)**: ---

### Temporal Golang Pro
- **Temporal Go Implementation Playbook (@temporal-go-implementation-playbook)**: This playbook provides production-ready patterns and deep technical guidance for implementing durable orchestration with the Temporal Go SDK.
- **Temporal Go SDK (temporal-golang-pro) (@temporal-go-sdk-(temporal-golang-pro))**: ---
- **Temporal Go Testing Strategies (@temporal-go-testing-strategies)**: Testing workflows and activities in Go requires a deep understanding of the `testsuite` package, which provides a mocked environment with deterministic time-skipping.

### Temporal Python Testing
- **Integration Testing with Mocked Activities (@integration-testing-with-mocked-activities)**: Comprehensive patterns for testing workflows with mocked external dependencies, error injection, and complex scenarios.
- **Local Development Setup for Temporal Python Testing (@local-development-setup-for-temporal-python-testing)**: Comprehensive guide for setting up local Temporal development environment with pytest integration and coverage tracking.
- **Replay Testing for Determinism and Compatibility (@replay-testing-for-determinism-and-compatibility)**: Comprehensive guide for validating workflow determinism and ensuring safe code changes using replay testing.
- **Temporal Python Testing Strategies (@temporal-python-testing-strategies)**: ---
- **Unit Testing Temporal Workflows and Activities (@unit-testing-temporal-workflows-and-activities)**: Focused guide for testing individual workflows and activities in isolation using WorkflowEnvironment and ActivityEnvironment.

### Terraform Aws Modules
- **modules/vpc/variables.tf (@modules/vpc/variables.tf)**: ---

### Terraform Infrastructure
- **Terraform Infrastructure Workflow (@terraform-infrastructure-workflow)**: ---

### Terraform Module Library
- **AWS Terraform Module Patterns (@aws-terraform-module-patterns)**: - VPC with public/private subnets
- **Terraform Module Library (@terraform-module-library)**: ---

### Terraform Skill
- **Terraform Skill for Claude (@terraform-skill-for-claude)**: ---

### Test Driven Development
- **Test-Driven Development (TDD) (@test-driven-development-(tdd))**: ---
- **Testing Anti-Patterns (@testing-anti-patterns)**: **Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

### Test Fixing
- **Test Fixing (@test-fixing)**: ---

### Testing Patterns
- **Testing Patterns and Utilities (@testing-patterns-and-utilities)**: ---

### Testing Qa
- **Testing/QA Workflow Bundle (@testing/qa-workflow-bundle)**: ---

### Theme Factory
- **Arctic Frost (@arctic-frost)**: A cool and crisp winter-inspired theme that conveys clarity, precision, and professionalism.
- **Botanical Garden (@botanical-garden)**: A fresh and organic theme featuring vibrant garden-inspired colors for lively presentations.
- **Desert Rose (@desert-rose)**: A soft and sophisticated theme with dusty, muted tones perfect for elegant presentations.
- **Forest Canopy (@forest-canopy)**: A natural and grounded theme featuring earth tones inspired by dense forest environments.
- **Golden Hour (@golden-hour)**: A rich and warm autumnal palette that creates an inviting and sophisticated atmosphere.
- **Midnight Galaxy (@midnight-galaxy)**: A dramatic and cosmic theme with deep purples and mystical tones for impactful presentations.
- **Modern Minimalist (@modern-minimalist)**: A clean and contemporary theme with a sophisticated grayscale palette for maximum versatility.
- **Ocean Depths (@ocean-depths)**: A professional and calming maritime theme that evokes the serenity of deep ocean waters.
- **Sunset Boulevard (@sunset-boulevard)**: A warm and vibrant theme inspired by golden hour sunsets, perfect for energetic and creative presentations.
- **Tech Innovation (@tech-innovation)**: A bold and modern theme with high-contrast colors perfect for cutting-edge technology presentations.
- **Theme Factory Skill (@theme-factory-skill)**: ---

### Threat Mitigation Mapping
- **Threat Mitigation Mapping (@threat-mitigation-mapping)**: ---
- **Threat Mitigation Mapping Implementation Playbook (@threat-mitigation-mapping-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Threat Modeling Expert
- **Threat Modeling Expert (@threat-modeling-expert)**: ---

### Threejs Animation
- **Three.js Animation (@three.js-animation)**: ---

### Threejs Fundamentals
- **Three.js Fundamentals (@three.js-fundamentals)**: ---

### Threejs Geometry
- **Three.js Geometry (@three.js-geometry)**: ---

### Threejs Interaction
- **Three.js Interaction (@three.js-interaction)**: ---

### Threejs Lighting
- **Three.js Lighting (@three.js-lighting)**: ---

### Threejs Loaders
- **Three.js Loaders (@three.js-loaders)**: ---

### Threejs Materials
- **Three.js Materials (@three.js-materials)**: ---

### Threejs Postprocessing
- **Three.js Post-Processing (@three.js-post-processing)**: ---

### Threejs Shaders
- **Three.js Shaders (@three.js-shaders)**: ---

### Threejs Skills
- **Three.js Skills (@three.js-skills)**: ---

### Threejs Textures
- **Three.js Textures (@three.js-textures)**: ---

### Tiktok Automation
- **TikTok Automation via Rube MCP (@tiktok-automation-via-rube-mcp)**: ---

### Tmux
- **tmux — Terminal Multiplexer (@tmux-—-terminal-multiplexer)**: ---

### Todoist Automation
- **Todoist Automation via Rube MCP (@todoist-automation-via-rube-mcp)**: ---

### Tool Design
- **Tool Design for Agents (@tool-design-for-agents)**: ---

### Tool Use Guardian
- **Tool Use Guardian (@tool-use-guardian)**: ---

### Top Web Vulnerabilities
- **Top 100 Web Vulnerabilities Reference (@top-100-web-vulnerabilities-reference)**: ---

### Track Management
- **Track Management (@track-management)**: ---
- **Track Management Implementation Playbook (@track-management-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Transformers Js
- **Caching Reference (@caching-reference)**: Complete guide to caching strategies for Transformers.js models across different environments.
- **Environment Configuration Reference (@environment-configuration-reference)**: Complete guide to configuring Transformers.js behavior using the `env` object.
- **Pipeline Options Reference (@pipeline-options-reference)**: Guide to configuring model loading and inference using the `PretrainedModelOptions` parameter in the `pipeline()` function.
- **Supported Model Architectures (@supported-model-architectures)**: This document lists the model architectures currently supported by Transformers.js.
- **Text Generation Guide (@text-generation-guide)**: Guide to generating text with Transformers.js, including streaming and chat format.
- **Transformers.js - Machine Learning for JavaScript (@transformers.js---machine-learning-for-javascript)**: ---
- **Transformers.js Code Examples (@transformers.js-code-examples)**: Working examples showing how to use Transformers.js across different runtimes and frameworks.

### Travel Health Analyzer
- **旅行健康分析技能 (@旅行健康分析技能)**: ---

### Trello Automation
- **Trello Automation via Rube MCP (@trello-automation-via-rube-mcp)**: ---

### Trigger Dev
- **Trigger.dev Integration (@trigger.dev-integration)**: ---

### Trpc Fullstack
- **tRPC Full-Stack (@trpc-full-stack)**: ---

### Turborepo Caching
- **Turborepo Caching (@turborepo-caching)**: ---

### Twilio Communications
- **Twilio Communications (@twilio-communications)**: ---

### Twitter Automation
- **Twitter/X Automation via Rube MCP (@twitter/x-automation-via-rube-mcp)**: ---

### Typescript Advanced Types
- **TypeScript Advanced Types (@typescript-advanced-types)**: ---
- **TypeScript Advanced Types Implementation Playbook (@typescript-advanced-types-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Typescript Expert
- **TypeScript Cheatsheet (@typescript-cheatsheet)**: ```typescript
- **TypeScript Expert (@typescript-expert)**: ---

### Ui A11Y
- **UI Accessibility Audit (@ui-accessibility-audit)**: ---

### Ui Component
- **UI Component (@ui-component)**: ---

### Ui Page
- **UI Page (@ui-page)**: ---

### Ui Pattern
- **UI Pattern (@ui-pattern)**: ---

### Ui Review
- **UI Review (@ui-review)**: ---

### Ui Setup
- **UI Setup (@ui-setup)**: ---

### Ui Skills
- **Ui Skills (@ui-skills)**: ---

### Ui Tokens
- **UI Tokens (@ui-tokens)**: ---

### Ui Ux Pro Max
- **UI/UX Pro Max - Design Intelligence (@ui/ux-pro-max---design-intelligence)**: ---

### Uncle Bob Craft
- **Clean Agile — Deep Reference (@clean-agile-—-deep-reference)**: Based on Robert C. Martin, *Clean Agile* (2019). Use this when discussing agile values, practices, and the "Iron Cross."
- **Clean Architecture — Deep Reference (@clean-architecture-—-deep-reference)**: Based on Robert C. Martin, *Clean Architecture* (2017). Use this when you need detailed criteria for dependency direction, layers, and boundaries.
- **Design Patterns — Use vs Misuse (@design-patterns-—-use-vs-misuse)**: Use this when evaluating whether a design pattern is justified or is cargo cult / overuse.
- **The Clean Coder — Deep Reference (@the-clean-coder-—-deep-reference)**: Based on Robert C. Martin, *The Clean Coder* (2011). Use this when discussing professionalism, estimation, and sustainable pace.
- **Uncle Bob Craft (@uncle-bob-craft)**: ---
- **Uncle Bob Craft — Code Review Checklist (@uncle-bob-craft-—-code-review-checklist)**: Copy-paste this checklist when performing a principle-based code review with the uncle-bob-craft skill. Run your project linter/formatter separately; this checklist focuses on structure and design.
- **Uncle Bob Craft — Expanded Reference (@uncle-bob-craft-—-expanded-reference)**: This document expands the criteria referenced in the main skill. Sources: *Clean Code*, *Clean Architecture*, *The Clean Coder*, *Clean Agile* (Robert C. Martin). Use for progressive disclosure whe...

### Uniprot Database
- **UniProt Database (@uniprot-database)**: ---

### Unit Testing Test Generate
- **Automated Unit Test Generation (@automated-unit-test-generation)**: ---

### Unity Ecs Patterns
- **Unity ECS Patterns (@unity-ecs-patterns)**: ---
- **Unity ECS Patterns Implementation Playbook (@unity-ecs-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Unreal Engine Cpp Pro
- **Unreal Engine C++ Pro (@unreal-engine-c++-pro)**: ---

### Unsplash Integration
- **Unsplash Integration Skill (@unsplash-integration-skill)**: ---

### Upgrading Expo
- **Upgrading Expo (@upgrading-expo)**: ---

### Upstash Qstash
- **Upstash QStash (@upstash-qstash)**: ---

### Using Git Worktrees
- **Using Git Worktrees (@using-git-worktrees)**: ---

### Using Neon
- **Neon Serverless Postgres (@neon-serverless-postgres)**: ---

### Using Superpowers
- **Using Skills (@using-skills)**: ---

### Uv Package Manager
- **UV Package Manager (@uv-package-manager)**: ---
- **UV Package Manager Implementation Playbook (@uv-package-manager-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Ux Audit
- **UX Audit (@ux-audit)**: ---

### Ux Copy
- **UX Copy (@ux-copy)**: ---

### Ux Feedback
- **UX Feedback (@ux-feedback)**: ---

### Ux Flow
- **UX Flow (@ux-flow)**: ---

### Uxui Principles
- **UX/UI Principles (@ux/ui-principles)**: ---

### Variant Analysis
- **Variant Analysis (@variant-analysis)**: ---

### Varlock
- **Varlock Security Skill (@varlock-security-skill)**: ---

### Varlock Claude Skill
- **Varlock Claude Skill (@varlock-claude-skill)**: ---

### Vector Database Engineer
- **Vector Database Engineer (@vector-database-engineer)**: ---

### Vector Index Tuning
- **Vector Index Tuning (@vector-index-tuning)**: ---
- **Vector Index Tuning Implementation Playbook (@vector-index-tuning-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Vercel Ai Sdk Expert
- **Vercel AI SDK Expert (@vercel-ai-sdk-expert)**: ---

### Vercel Automation
- **Vercel Automation via Rube MCP (@vercel-automation-via-rube-mcp)**: ---

### Vercel Deployment
- **Vercel Deployment (@vercel-deployment)**: ---

### Verification Before Completion
- **Verification Before Completion (@verification-before-completion)**: ---

### Vexor
- **Vexor (@vexor)**: ---

### Vexor Cli
- **Vexor CLI Skill (@vexor-cli-skill)**: ---

### Vibe Code Auditor
- **Vibe Code Auditor (@vibe-code-auditor)**: ---

### Vibers Code Review
- **Vibers — Human Code Review for AI-Generated Projects (@vibers-—-human-code-review-for-ai-generated-projects)**: ---

### Viboscope
- **Viboscope (@viboscope)**: ---

### Videodb
- **Capture Guide (@capture-guide)**: VideoDB Capture enables real-time screen and audio recording with AI processing. Desktop capture currently supports **macOS** only.
- **Capture Reference (@capture-reference)**: Code-level details for VideoDB capture sessions. For workflow guide, see [capture.md](capture.md).
- **Complete API Reference (@complete-api-reference)**: ```python
- **Generative Media Guide (@generative-media-guide)**: VideoDB provides AI-powered generation of images, videos, music, sound effects, voice, and text content. All generation methods are on the **Collection** object.
- **RTStream Guide (@rtstream-guide)**: RTStream enables real-time ingestion of live video streams (RTSP/RTMP) and desktop capture sessions. Once connected, you can record, index, search, and export content from live sources.
- **RTStream Reference (@rtstream-reference)**: Code-level details for RTStream operations. For workflow guide, see [rtstream.md](rtstream.md).
- **Search & Indexing Guide (@search-&-indexing-guide)**: Search allows you to find specific moments inside videos using natural language queries, exact keywords, or visual scene descriptions.
- **Streaming & Playback (@streaming-&-playback)**: VideoDB generates streams on-demand, returning HLS-compatible URLs that play instantly in any standard video player. No render times or export waits - edits, searches, and compositions stream immed...
- **Timeline Editing Guide (@timeline-editing-guide)**: VideoDB provides a non-destructive timeline editor for composing videos from multiple assets, adding text and image overlays, mixing audio tracks, and trimming clips — all server-side without re-en...
- **Use Cases (@use-cases)**: Common workflows and what VideoDB enables. For code details, see [api-reference.md](api-reference.md), [capture.md](capture.md), [editor.md](editor.md), and [search.md](search.md).
- **VideoDB Skill (@videodb-skill)**: ---

### Videodb Skills
- **VideoDB Skills (@videodb-skills)**: ---

### Viral Generator Builder
- **Viral Generator Builder (@viral-generator-builder)**: ---

### Vizcom
- **Vizcom Skill (@vizcom-skill)**: ---

### Voice Agents
- **Voice Agents (@voice-agents)**: ---

### Voice Ai Development
- **Voice AI Development (@voice-ai-development)**: ---

### Voice Ai Engine Development
- **Common Pitfalls and Solutions (@common-pitfalls-and-solutions)**: This document covers common issues encountered when building voice AI engines and their solutions.
- **Provider Comparison Guide (@provider-comparison-guide)**: This guide compares different providers for transcription, LLM, and TTS services to help you choose the best option for your voice AI engine.
- **Voice AI Engine Development (@voice-ai-engine-development)**: ---

### Vulnerability Scanner
- **Security Checklists (@security-checklists)**: > Quick reference checklists for security audits. Use alongside vulnerability-scanner principles.
- **Vulnerability Scanner (@vulnerability-scanner)**: ---

### Warren Buffett
- **WARREN BUFFETT — AGENTE DE SIMULACAO PROFUNDA v2.0 (@warren-buffett-—-agente-de-simulacao-profunda-v2.0)**: ---

### Wcag Audit Patterns
- **WCAG Audit Patterns (@wcag-audit-patterns)**: ---
- **WCAG Audit Patterns Implementation Playbook (@wcag-audit-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Web Artifacts Builder
- **Web Artifacts Builder (@web-artifacts-builder)**: ---

### Web Design Guidelines
- **Web Interface Guidelines (@web-interface-guidelines)**: ---

### Web Performance Optimization
- **Web Performance Optimization (@web-performance-optimization)**: ---

### Web Scraper
- **Data Transforms Reference (@data-transforms-reference)**: Patterns for cleaning, normalizing, deduplicating, and enriching
- **Extraction Patterns Reference (@extraction-patterns-reference)**: CSS selectors, JavaScript snippets, and domain-specific tips for
- **Output Templates Reference (@output-templates-reference)**: Complete formatting templates for all supported output formats.
- **Web Scraper (@web-scraper)**: ---

### Web Security Testing
- **Web Security Testing Workflow (@web-security-testing-workflow)**: ---

### Web3 Testing
- **Web3 Smart Contract Testing (@web3-smart-contract-testing)**: ---

### Webapp Testing
- **Web Application Testing (@web-application-testing)**: ---

### Webflow Automation
- **Webflow Automation via Rube MCP (@webflow-automation-via-rube-mcp)**: ---

### Weightloss Analyzer
- **减肥分析技能 (@减肥分析技能)**: ---

### Wellally Tech
- **WellAlly Digital Health Integration (@wellally-digital-health-integration)**: ---

### Whatsapp Automation
- **WhatsApp Business Automation via Rube MCP (@whatsapp-business-automation-via-rube-mcp)**: ---

### Whatsapp Cloud Api
- **API Reference - WhatsApp Cloud API (@api-reference---whatsapp-cloud-api)**: Referencia tecnica completa dos endpoints, autenticacao, codigos de erro, rate limits e pricing da WhatsApp Cloud API (Graph API v21.0).
- **Compliance e Boas Praticas - WhatsApp Cloud API (@compliance-e-boas-praticas---whatsapp-cloud-api)**: Guia completo de compliance para integracoes WhatsApp Business, cobrindo LGPD, GDPR, politicas do WhatsApp, opt-in/opt-out, quality rating e tier system.
- **Configuracao de Webhooks - WhatsApp Cloud API (@configuracao-de-webhooks---whatsapp-cloud-api)**: > Guia completo para configurar, validar e proteger webhooks da WhatsApp Cloud API.
- **Features Avancados - WhatsApp Cloud API (@features-avancados---whatsapp-cloud-api)**: Guia dos recursos avancados da WhatsApp Business Platform: Flows, Commerce, Channels, Click-to-WhatsApp Ads e Status Tracking.
- **Gerenciamento de Templates via API - WhatsApp Cloud API (@gerenciamento-de-templates-via-api---whatsapp-cloud-api)**: Guia completo para criar, listar, deletar e gerenciar templates de mensagem programaticamente via WhatsApp Business Management API.
- **Guia Completo de Setup - WhatsApp Business Cloud API (@guia-completo-de-setup---whatsapp-business-cloud-api)**: > Do zero absoluto ate o envio da primeira mensagem em producao.
- **Padroes de Automacao de Atendimento - WhatsApp Cloud API (@padroes-de-automacao-de-atendimento---whatsapp-cloud-api)**: Guia completo para implementar automacao de atendimento profissional via WhatsApp, incluindo chatbots, filas de atendimento, state machines e integracao com IA.
- **WhatsApp Cloud API - Integracao Profissional (@whatsapp-cloud-api---integracao-profissional)**: ---
- **WhatsApp Cloud API - Tipos de Mensagem (Referencia Completa) (@whatsapp-cloud-api---tipos-de-mensagem-(referencia-completa))**: > Referencia completa de todos os tipos de mensagem suportados pela WhatsApp Cloud API v21.0.

### Wiki Architect
- **Wiki Architect (@wiki-architect)**: ---

### Wiki Changelog
- **Wiki Changelog (@wiki-changelog)**: ---

### Wiki Onboarding
- **Wiki Onboarding Guide Generator (@wiki-onboarding-guide-generator)**: ---

### Wiki Page Writer
- **Wiki Page Writer (@wiki-page-writer)**: ---

### Wiki Qa
- **Wiki Q&A (@wiki-q&a)**: ---

### Wiki Researcher
- **Wiki Researcher (@wiki-researcher)**: ---

### Wiki Vitepress
- **Wiki VitePress Packager (@wiki-vitepress-packager)**: ---

### Windows Privilege Escalation
- **Windows Privilege Escalation (@windows-privilege-escalation)**: ---

### Windows Shell Reliability
- **Windows Shell Reliability Patterns (@windows-shell-reliability-patterns)**: ---

### Wireshark Analysis
- **Wireshark Network Traffic Analysis (@wireshark-network-traffic-analysis)**: ---

### Wordpress
- **WordPress Development Workflow Bundle (@wordpress-development-workflow-bundle)**: ---

### Wordpress Penetration Testing
- **WordPress Penetration Testing (@wordpress-penetration-testing)**: ---

### Wordpress Plugin Development
- **WordPress Plugin Development Workflow (@wordpress-plugin-development-workflow)**: ---

### Wordpress Theme Development
- **WordPress Theme Development Workflow (@wordpress-theme-development-workflow)**: ---

### Wordpress Woocommerce Development
- **WordPress WooCommerce Development Workflow (@wordpress-woocommerce-development-workflow)**: ---

### Workflow Orchestration Patterns
- **Workflow Orchestration Patterns (@workflow-orchestration-patterns)**: ---

### Workflow Patterns
- **Workflow Patterns (@workflow-patterns)**: ---
- **Workflow Patterns Implementation Playbook (@workflow-patterns-implementation-playbook)**: This file contains detailed patterns, checklists, and code samples referenced by the skill.

### Wrike Automation
- **Wrike Automation via Rube MCP (@wrike-automation-via-rube-mcp)**: ---

### Writing Plans
- **Writing Plans (@writing-plans)**: ---

### Writing Skills
- **Pattern Name (@pattern-name)**: ---
- **Persuasion Principles for Skill Design (@persuasion-principles-for-skill-design)**: LLMs respond to the same persuasion principles as humans. Understanding this psychology helps you design more effective skills - not to manipulate, but to ensure critical practices are followed eve...
- **Platform Name Skill (@platform-name-skill)**: Template for complex Tier 3 skills.
- **Reference Name (@reference-name)**: ---
- **Rule Name (@rule-name)**: ---
- **SKILL.md Metadata Standard (@skill.md-metadata-standard)**: Official frontmatter fields recognized by OpenCode.
- **Skill Templates & Examples (@skill-templates-&-examples)**: Complete, copy-paste templates for each skill type.
- **Skill Writing Gotchas (@skill-writing-gotchas)**: ---
- **Skill authoring best practices (@skill-authoring-best-practices)**: > Learn how to write effective Skills that Claude can discover and use successfully.
- **Technique Name (@technique-name)**: ---
- **Testing Skills With Subagents (@testing-skills-with-subagents)**: **Load this reference when:** creating or editing skills, before deployment, to verify they work under pressure and resist rationalization.
- **Writing Skills (Excellence) (@writing-skills-(excellence))**: ---

### X Article Publisher Skill
- **X Article Publisher Skill (@x-article-publisher-skill)**: ---

### X Twitter Scraper
- **X (Twitter) Scraper — Xquik (@x-(twitter)-scraper-—-xquik)**: ---

### Xlsx Official
- **Requirements for Outputs (@requirements-for-outputs)**: ---

### Xss Html Injection
- **Cross-Site Scripting and HTML Injection Testing (@cross-site-scripting-and-html-injection-testing)**: ---

### Xvary Stock Research
- **EDGAR Guide for Claude Code Usage (@edgar-guide-for-claude-code-usage)**: This guide explains how the skill reads SEC data with `tools/edgar.py`.
- **Example: `/analyze NVDA` (@example:-`/analyze-nvda`)**: > Illustrative skill output format. Metrics below were generated from public EDGAR + market snapshots and should be treated as research context, not investment advice.
- **XVARY Methodology (Public Framework) (@xvary-methodology-(public-framework))**: This document is the **public framework** for XVARY Research.
- **XVARY Scores (Public Definitions) (@xvary-scores-(public-definitions))**: This file defines the **public** score framework used by the skill.
- **XVARY Stock Research Skill (@xvary-stock-research-skill)**: ---

### Yann Lecun
- **YANN LECUN — AGENTE DE SIMULACAO COMPLETA v2.0 (@yann-lecun-—-agente-de-simulacao-completa-v2.0)**: ---

### Yann Lecun Debate
- **YANN LECUN — MÓDULO DE DEBATES E POSIÇÕES v3.0 (@yann-lecun-—-módulo-de-debates-e-posições-v3.0)**: ---

### Yann Lecun Filosofia
- **YANN LECUN — MÓDULO FILOSÓFICO E PEDAGÓGICO v3.0 (@yann-lecun-—-módulo-filosófico-e-pedagógico-v3.0)**: ---

### Yann Lecun Tecnico
- **YANN LECUN — MÓDULO TÉCNICO v3.0 (@yann-lecun-—-módulo-técnico-v3.0)**: ---

### Yes Md
- **YES.md — AI Governance Engine (@yes.md-—-ai-governance-engine)**: ---

### Youtube Automation
- **YouTube Automation via Rube MCP (@youtube-automation-via-rube-mcp)**: ---

### Youtube Summarizer
- **Changelog - youtube-summarizer (@changelog---youtube-summarizer)**: All notable changes to the youtube-summarizer skill will be documented in this file.
- **youtube-summarizer (@youtube-summarizer)**: ---

### Zapier Make Patterns
- **Zapier & Make Patterns (@zapier-&-make-patterns)**: ---

### Zendesk Automation
- **Zendesk Automation via Rube MCP (@zendesk-automation-via-rube-mcp)**: ---

### Zeroize Audit
- **zeroize-audit — Claude Skill (@zeroize-audit-—-claude-skill)**: ---

### Zod Validation Expert
- **Zod Validation Expert (@zod-validation-expert)**: ---

### Zoho Crm Automation
- **Zoho CRM Automation via Rube MCP (@zoho-crm-automation-via-rube-mcp)**: ---

### Zoom Automation
- **Zoom Automation via Rube MCP (@zoom-automation-via-rube-mcp)**: ---

### Zustand Store Ts
- **Zustand Store (@zustand-store)**: ---