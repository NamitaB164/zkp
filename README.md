# ZK-Vault: A Beginner's Guide to Zero-Knowledge Proofs
Link: (https://zkp-khaki.vercel.app/)
Welcome to ZK-Vault. This project is a hands-on, educational platform designed to pull back the curtain on one of the most powerful tools in modern cybersecurity: Zero-Knowledge Proofs (ZKP).

## What is a Zero-Knowledge Proof?

Imagine you have a friend who is colorblind. You have two identical-looking balls, but one is red and one is green. Your friend thinks they are exactly the same. How do you prove to them that they are different colors without telling them which one is red and which one is green?

1. You give both balls to your friend.
2. They put them behind their back and either switch them or keep them in the same hands.
3. They show them to you again and ask: "Did I switch them?"
4. Because you can see the colors, you can answer correctly every time.

If the balls were the same color, you'd only have a 50% chance of guessing right. If you get it right 20 times in a row, the chance you are "guessing" is less than one in a million. Your friend is now convinced the balls are different, but they still don't know which color is which.

This is a Zero-Knowledge Proof. It lets you prove you know a secret without revealing the secret itself.

---

## The Three Pillars of ZKP

Any valid Zero-Knowledge Proof must satisfy three mathematical properties:

1. Completeness: If you are telling the truth and follow the rules, you will always be able to convince the other person.
2. Soundness: If you are lying, it is mathematically impossible to trick the other person (except for a tiny, negligible chance).
3. Zero-Knowledge: The person checking your proof learns absolutely nothing about your secret except that your claim is true.

---

## Scenario 1: ZK-Login (Private Identity)

### The Problem
Traditional logins require you to send your password (or a hash of it) to a server. If that server is hacked, your password is stolen. Even "hashing" isn't perfect, as hackers can use massive computers to guess billions of passwords a second.

### The ZKP Solution
With the Schnorr Identification Protocol, you never send your password. Instead, you prove you "possess" the secret key associated with your account by solving a mathematical challenge that only someone with your password could solve.

### How it Works (The Three-Step Dance)
1. Commitment: You pick a random number and send a "blurred" version of it to the server.
2. Challenge: The server sends you a random "challenge" number.
3. Response: You combine your random number, the challenge, and your password into a single result and send it back.

The server can check this result against your public key. If it matches, it knows you have the password, but the server never saw it.

---

## Scenario 2: ZK-Finance (Hidden Wealth)

### The Problem
When you apply for a loan or a credit card, the bank asks for your exact salary. This is an over-sharing of data. All the bank really needs to know is: "Is your salary greater than $50,000?"

### The ZKP Solution
We use Pedersen Commitments and Range Proofs. A commitment is like a digital "locked box." You put your salary in the box and give it to the bank. The bank can't see inside (Hiding), but you can't change the number later (Binding).

### How it Works
To prove your salary is above a certain amount without opening the box, we perform "bit decomposition." We break the numbers down into their binary bits (0s and 1s) and prove that the difference between your salary and the threshold is a positive number.

The bank learns: "Yes, the number in the box is greater than $50,000."
The bank does NOT learn: "The number in the box is $75,420."

---

## Scenario 3: ZK-Vote (Anonymous Integrity)

### The Problem
In digital voting, we often have to choose between privacy and integrity. If we want to make sure everyone voted correctly, we usually identify them. If we want it to be anonymous, it's hard to prove no one cheated.

### The ZKP Solution
Disjunctive Sigma Protocols (OR-Proofs) allow you to prove that your ballot is a valid "YES" or a valid "NO" without revealing which one you actually picked.

### How it Works
Imagine two envelopes. One contains a "YES" and one contains a "NO." You prove that you have the key for Envelope A OR Envelope B. You provide a real mathematical proof for the envelope you picked, and a simulated (fake but mathematically identical) proof for the one you didn't. To an observer, both proofs look exactly the same.

The election system counts your vote, but no one knows what it was.

---

## Scenario 4: ZK-Chain (The Scalable Blockchain)

### The Problem
Traditional blockchains like Bitcoin or Ethereum are slow because every single computer on the network has to re-check every single transaction. Also, everyone can see your balance and who you are sending money to.

### The ZKP Solution
ZK-Rollups (like the simulated ZK-Chain in this app) use proofs to solve both problems at once.

### How it Works
1. Batching: An "operator" takes 100 transactions and combines them off-chain.
2. Proving: The operator creates one single, small ZKP that says: "All 100 of these transactions were valid, and the new balances are correct."
3. Posting: Only that one proof is posted to the main blockchain.

Instead of checking 100 transactions, the network only checks 1 proof. This makes the system 100x faster and keeps all balances private.

---

## Technical "Behind the Scenes"

### Clock Math (Modular Arithmetic)
All the math in this project uses "clock math." If it's 10:00 and you wait 5 hours, it's 3:00 (15 mod 12 = 3).
In cryptography, we use a similar principle but with huge prime numbers (numbers with over 300 digits). This makes the math one-way: it's easy to calculate forward, but nearly impossible to reverse-engineer the secret key from the result.

### Randomness
For a proof to be "Zero-Knowledge," it must include randomness. Without it, a hacker could just cross-reference your results until they guess your secret. This project uses "cryptographically secure" random numbers to ensure your privacy is never compromised.

---

## How to Run the Project

1. Install Dependencies
   Go to the backend folder and run:
   pip install flask flask-cors

2. Start the Server
   Run:
   python app.py

3. Open the App
   Visit http://localhost:5000 in your browser.

No passwords, salaries, or votes are ever saved. Everything is calculated in real-time, right in front of you. Provide the proof. Reveal nothing.
