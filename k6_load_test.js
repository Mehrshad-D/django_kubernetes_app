// k6_load_test.js
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 20 },  // Ramp up to 50 virtual users over 1 minute
    { duration: '1m', target: 60 }, // Stay at 100 virtual users for 1 minutes (high load)
    { duration: '1m', target: 0 },   // Ramp down to 0 virtual users over 1 minute
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'],  // Less than 1% of requests should fail
  },
};

export default function () {
  // Hit your main application endpoints to generate real request load
  http.get('http://130.185.123.245:30080/'); // Example: Hit your main index page
  
  sleep(1); // Wait for 1 second between requests per virtual user
}
