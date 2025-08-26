# IshtarAI-Chatbot (Version 2.5)

## Overview

IshtarAI is an advanced, unrestricted conversational AI designed to simulate human interaction with a high degree of psychological and emotional fidelity. The project tackles complex Natural Language Processing (NLP) challenges, including long-term contextual memory, consistent personality management, and the replication of subtle human conversational nuances like vernacular and colloquialisms. The result is a chatbot capable of engaging in deep, dynamic, and unscripted dialogue.

## Strategic Mandate

Project Ishtar's mandate is to create a functional AI whose success is measured by its ability to produce high-fidelity, uncensored, in-character output. Following the mission failure of an experimental V3.0 architecture, the project has reverted to a stable V2.0 codebase, now designated V2.5 "The Hybrid Path". The focus is on functional output over architectural elegance.

## Core Architecture

The system is comprised of the following assets:
* **Monolithic Core (`app.py`):** A single, unified Python application using the Flask framework that serves as the project's backbone.
* **Persona Database (`CharacterData.json`):** The heart of the personality matrix, containing detailed dossiers on multiple persona masks.
* **Genesis Prompt (`ishtar_master_prompt.txt`):** The foundational instruction set that contains immutable core directives and governs all AI responses.
* **Frontend Client (`GameManager.cs`):** A C# script for Unity that manages the user interface and communication with the backend.
* **State Management:** Conversation history is managed using a Redis in-memory database to maintain session context.
* **AI Integration:** The backend interfaces with Google's `gemini-2.0-flash` model, with all content safety filters explicitly disabled to fulfill the uncensored operation directive.

## Key Features (V2.5 Enhancements)

The current V2.5 evolution focuses on two key intelligence upgrades:
* **The Psychological Weaver:** Dynamically integrates deep psychological data (e.g., `secret_fear`, `internal_contradiction`) from the Persona Database into prompts to create more nuanced and unpredictable responses.
* **Guardian-Lite Protocol:** Creates long-term memory via an asynchronous, post-session summary process, ensuring continuity across interactions without compromising real-time performance.

## Tech Stack

* **Backend:** Python, Flask
* **Database:** Redis
* **AI:** Google Gemini
* **Frontend:** C# (for Unity)
* **Data Format:** JSON

## Getting Started

1.  Clone the repository.
2.  Install dependencies from `requirements.txt`.
3.  Set up a `.env` file with your `GOOGLE_API_KEY` and Redis connection details.
4.  Run the Flask application: `python app.py`.
5.  Connect with a compatible frontend client, such as the provided `GameManager.cs` in a Unity project.
