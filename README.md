# Queue11 (Q11)

Queue-1-1 is an intelligent triage system designed to assist 911 responders in prioritizing emergency calls during periods of high traffic. Using machine learning and AI, Q11 analyzes call data in real-time to ensure critical situations receive immediate attention, helping save lives in high-stress environments.

## Inspiration

Our inspiration for Queue-1-1 came from witnessing the immense strain on small-town 911 call centers, where long wait times during emergencies can become life-threatening. Seeing these challenges in smaller communities, and recognizing that large cities face similar problems, inspired us to create a solution to help prioritize calls and optimize response times.

## Features

- **AI-powered call triage:** Leverages machine learning to prioritize emergency calls.
- **Cloud telephony integration:** Uses Plivo for automated prompts and call handling.
- **Real-time call analysis:** Transcribes and processes call recordings to assign priority scores.
- **Dashboard interface:** Displays caller details, call times, and emergency descriptions in a simple format for 911 operators.
- **Duplicate call grouping:** Groups related incidents during crises to streamline dispatcher workload.
- **Automated call-backs:** Notifies callers that their information was successfully captured.

## How It Works

Queue-1-1 operates by recording and analyzing incoming 911 calls to assess their urgency. The system:
1. Plays automated messages to prompt callers to provide essential information (name, address, emergency description).
2. Transcribes call recordings using OpenAI's Whisper API.
3. Uses GPT-3.5 Turbo to extract key information from the transcription.
4. Runs a machine learning model (Random Forest Classifier) to assign a priority score to each call based on the extracted data.
5. Displays the prioritized calls in a dashboard for dispatchers, allowing for efficient crisis management.
6. Calls back the caller using Plivo to confirm that their information has been logged.

## Technologies Used

- **Backend:** Python, Pandas, Scikit-learn, Random Forest Classifier, Plivo, AWS S3
- **Machine Learning:** OpenAI Whisper, GPT-3.5 Turbo, TF-IDF vectorizer
- **Frontend:** JavaScript, HTML, CSS
- **UI/Prototyping:** Figma
- **Hosting:** Vercel

## Challenges We Faced

- **Telephony integration issues:** Integrating Plivo and AWS voice services was challenging due to low recording quality and API limitations.
- **Data handling:** Optimizing the machine learning model for unstructured and imbalanced emergency data was another significant hurdle.
- **Feature engineering:** Creating an accurate and reliable priority classification system involved extensive data preparation and engineering.

## Achievements

- We successfully integrated multiple complex technologies (cloud telephony, AI, machine learning) into one cohesive system.
- Expanded our dataset from 2.9 million to 7 million call entries using SMOTE, significantly improving model accuracy (93.71%).
- Developed a fully functional dashboard that improves emergency call triage efficiency.

## What We Learned

- We gained a deeper understanding of telephony APIs, specifically how to integrate and troubleshoot Plivo with OpenAI’s Whisper and GPT-3.5 Turbo.
- We learned how to handle large, imbalanced datasets for machine learning tasks, enhancing our technical skills in both front-end and back-end development.
- We strengthened our knowledge of JavaScript, HTML, and CSS while working with real-time AI-driven features.

## What's Next

- **Advanced speech recognition:** We aim to improve speech-to-text accuracy by incorporating more sophisticated models.
- **Location-based services:** Integrating location data to better identify nearby emergency responders.
- **Historical data analysis:** Utilizing past emergency data to further refine call prioritization.
- **Resource allocation:** Adding features to track available emergency resources (e.g., fire trucks, ambulances) and incorporate them into triage decisions.
