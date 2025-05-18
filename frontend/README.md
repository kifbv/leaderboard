# Ping-Pong Leaderboard Frontend

This is the frontend application for the Ping-Pong Leaderboard system.

## Features

- Player rankings and leaderboards
- Game tracking and results
- Tournament management
- Authentication with Google OAuth
- Admin functionality for site management

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- AWS account with Cognito configured

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy the environment variables template:
   ```bash
   cp .env.example .env.local
   ```

3. Update the environment variables in `.env.local` with your values.

4. Start the development server:
   ```bash
   npm start
   ```

### Configuration

This application uses AWS Amplify for authentication. The configuration is stored in `src/utils/amplify-config.ts`.

**Important:** Before deploying to production:

1. Set up a Cognito domain in AWS Console
2. Update the domain, redirectSignIn and redirectSignOut URLs in the configuration
3. Ensure ADMIN_EMAILS environment variable is set with comma-separated admin email addresses

### Deployment

The application is automatically deployed to AWS S3 and distributed via CloudFront when code is pushed to the main branch.

#### GitHub Secrets Required:

- `AWS_ACCESS_KEY_ID`: AWS access key with S3 and CloudFront permissions
- `AWS_SECRET_ACCESS_KEY`: Corresponding AWS secret key
- `ADMIN_EMAILS`: Comma-separated list of admin email addresses

## Project Structure

- `/src/api`: API client and service functions
- `/src/components`: Reusable UI components
- `/src/context`: React context for state management
- `/src/pages`: Main application pages
- `/src/types`: TypeScript type definitions
- `/src/utils`: Utility functions and helpers

## Available Scripts

- `npm start`: Run the development server
- `npm test`: Run tests
- `npm run build`: Build for production
- `npm run eject`: Eject from Create React App

## Authentication Flow

1. User clicks "Sign In with Google" button
2. User is redirected to Cognito hosted UI
3. After authentication, user is redirected back to the callback URL
4. Amplify processes the authentication response
5. User is redirected to the home page

## Access Control

- Regular users can view leaderboards and their own statistics
- Admin users (defined by the ADMIN_EMAILS environment variable) have access to site management and tournament creation functions
