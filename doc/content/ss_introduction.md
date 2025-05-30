# Solana/Program Development Basics/Introduction

Student: "Teacher, I just read the little story **Ada and the Thai Baht Coin Dilemma**, and it was super interesting! I didn't realize writing a Baht coin program on Solana could run into such real-world problems with address management."

Teacher: "Haha, that's the first big hurdle for many Solana beginners. It's not just about getting the program to run, it's all about how you manage the data."

Student: "I'm really curious about how she used PDAs to solve the problem. I've learned Ethereum before, and I could directly store any key/value data in an account. For example, I could design a key as an account address and a value as a number to record how much money everyone has. But on Solana, it seems like you have to handle all of that yourself?"

Teacher: "Exactly. Solana's smart contracts won't automatically keep track of how much money everyone has. You have to design the data accounts yourself, define the data structures, and set the permissions."

Student: "It feels like building blocks, but you also have to draw your own blueprints. So the Thai Baht Coin program had to fully implement its own balance and transfer logic?"

Teacher: "Yes, Ada assigned each user a PDA as their account to store their Thai Baht balance, so there's no need to manually tell others where their money is. This is a very common trick on Solana."

Student: "I want to try building something myself! Maybe not a Thai Baht coin, but how about a Bubble Coin? Like, each interaction creates a little bubble…"

Teacher: "That's creative! So in this chapter, let's start with the basics of writing Solana programs. First, I'll show you how to store data on-chain, and then you can slowly build your own bubble universe."

Student: "Sounds awesome!"
