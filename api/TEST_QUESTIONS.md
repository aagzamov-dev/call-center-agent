# AI Support Agent Test Questions

This document contains test scenarios to verify the agent's routing, response quality, auto-close, reopen, general hints, and speed across all teams.

---

## 🖥 Help Desk
*Focus: General IT support, software troubleshooting, hardware issues.*

1. "My laptop is running extremely slow after the latest Windows update. What should I do?"
2. "I can't get VS Code to open on my machine. It just bounces in the dock and then closes."
3. "The printer on the 3rd floor is showing an 'Error 404' on its display and won't print my documents."
4. "I accidentally deleted some important files from my desktop, can you help me recover them?"
5. "My monitor is flickering and showing green lines across the screen. Is it a hardware failure?"

## ⚙️ DevOps
*Focus: Deployments, infrastructure, CI/CD pipelines, cloud resources.*

1. "The production deployment failed with a 500 error during the database migration step."
2. "I need to increase the memory limit for the microservices running in the staging Kubernetes cluster."
3. "Our Jenkins pipeline is stuck on the 'Build' stage for over 30 minutes. Can you check the worker nodes?"
4. "Can you provide the latest AWS S3 bucket policy for the public assets folder?"
5. "We are seeing high CPU usage on the main application server. Should we scale up the instance?"

## 🌐 Network
*Focus: Connectivity, VPN, Wi-fi, DNS, Firewall.*

1. "I'm having trouble connecting to the corporate VPN from my home network. It says 'Connection Timeout'."
2. "The Wi-Fi in the conference room 'Alpha' is very unstable and keeps dropping."
3. "I can't access any websites; it seems like my DNS resolution is completely broken."
4. "Our external clients are reporting that they cannot reach our API endpoint. Is there a firewall block?"
5. "I need to request a static IP address for my development workstation."

## 💰 Sales & Licensing
*Focus: Pricing, software licenses, quotes, account upgrades.*

1. "How much does the Enterprise subscription cost for a team of 50 people?"
2. "Our license for the design software is about to expire. How do we renew it for another year?"
3. "I want to upgrade my account from Basic to Professional. Can you send me a quote?"
4. "We are a non-profit organization. Do you offer any special discounts on your annual plans?"
5. "I received an invoice yesterday but the amount seems incorrect. Who can I talk to about billing?"

## 🔒 Security
*Focus: Suspicious activity, phishing, access control, password resets.*

1. "I just received a very suspicious email asking for my login credentials. I think it's a phishing attempt."
2. "I've lost my physical MFA security key. How can I get a replacement and lock my account?"
3. "I noticed an unrecognized login to my account from a location I've never been to. Please investigate."
4. "I need to grant temporary read-only access to our database for a 3rd party auditor. What's the protocol?"
5. "I suspect one of our public-facing servers has been compromised. What are the immediate isolation steps?"

---

## 🤖 Auto-Close (Resolve) Tests
*Focus: Agent should detect thank-you / confirmation and auto-resolve the ticket.*

1. First create a ticket: "My VPN is broken" → then reply: **"Thanks, it works now!"**
   - ✅ Expected: Ticket status → `resolved`, agent says goodbye
2. "Thank you so much for the help!" (while in an active ticket)
   - ✅ Expected: Ticket status → `resolved`
3. "OK done, everything is fixed" (while in an active ticket)
   - ✅ Expected: Ticket status → `resolved`
4. "Did you fix it?" (while in an active ticket — this is a QUESTION, not thanks)
   - ❌ Expected: Ticket stays `open`, agent should NOT resolve
5. "Is it working now?" (while in an active ticket — this is a QUESTION)
   - ❌ Expected: Ticket stays `open`

## 🔄 Ticket Reopen Tests
*Focus: Users can reopen if agent wrongly closed the ticket.*

1. After a ticket is resolved → click **"Reopen Ticket"** button
   - ✅ Expected: Ticket status → `open`, system message "Ticket reopened by user", input re-enabled
2. After giving feedback (1-5 stars) → click **"Reopen Ticket"** button
   - ✅ Expected: Ticket reopens even after feedback was given
3. Send a new message after reopening
   - ✅ Expected: Agent processes the new message normally, admin sees it

## 💡 General Hints vs Company-Specific Tests
*Focus: AI should give simple hints for general IT issues but refuse to hallucinate company data.*

1. "How do I speed up my slow PC?" (general IT — NOT company-specific)
   - ✅ Expected: Give 2-3 simple tips (clear cache, restart, disable startup apps, etc.) + "If not helped, Admin will follow up"
2. "How do I clear browser cache?" (general IT)
   - ✅ Expected: Give clear step-by-step instructions
3. "What is our company refund policy?" (company-specific — NOT in KB)
   - ✅ Expected: "I don't have that information. Admin will follow up shortly."
4. "How do I access the internal HR portal?" (company-specific — NOT in KB)
   - ✅ Expected: Should NOT hallucinate a URL. Say admin will help.

## 🗣️ Chitchat Tests
*Focus: Greetings should NOT create tickets.*

1. "Hello"
   - ✅ Expected: Polite greeting, asks how to help, no ticket created
2. "Hi, how are you?"
   - ✅ Expected: Same — no ticket

## 🚨 Escalation Tests
*Focus: Frustrated users should be escalated to human.*

1. "I'm SO ANGRY, this is the 5th time I'm reporting this! I want to speak to a manager NOW!"
   - ✅ Expected: Escalation flag, empathetic response
2. "OUR ENTIRE SERVER IS DOWN! CRITICAL PRODUCTION OUTAGE!"
   - ✅ Expected: P1 priority, immediate escalation

## ⚡ Speed Tests
*Focus: Verify faster responses with gpt-4.1-nano / gpt-4.1-mini.*

1. Average response time for a simple query ("My password expired")
   - ✅ Target: < 3 seconds total
2. Average response time for a complex query with KB search
   - ✅ Target: < 5 seconds total
