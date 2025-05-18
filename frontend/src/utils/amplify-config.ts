import { Amplify } from 'aws-amplify';

// Configure Amplify
export const configureAmplify = () => {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: 'eu-central-1_7RzmyoEBQ',
        userPoolClientId: '2j7ijn7pgdtq724vgedldh2p5n',
        loginWith: {
          oauth: {
            domain: 'leaderboard-users-dev.auth.eu-central-1.amazoncognito.com',
            scopes: ['email', 'profile', 'openid'],
            redirectSignIn: ['https://d1wjr2jr559qzz.cloudfront.net/callback'],
            redirectSignOut: ['https://d1wjr2jr559qzz.cloudfront.net'],
            responseType: 'code'
          }
        }
      }
    },
    API: {
      REST: {
        LeaderboardAPI: {
          endpoint: 'https://fx3sr38767.execute-api.eu-central-1.amazonaws.com/dev'
        }
      }
    }
  });
};