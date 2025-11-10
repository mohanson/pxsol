# Solana/More Developer Tools/Introduction

It was the second-to-last class of the term, and the sun in the classroom felt a bit lazy. A student spun a pen quickly between his fingers, eyes absent.

Student: "Teacher, I wrote a few contracts and can send transactions now. I think I've got a basic understanding of the Solana network. But I still feel like something's missing?"

Teacher: "That's a normal doubt. You're missing an understanding of the Solana community's tooling. Aren't you curious? What the Solana core team is building right now, what others in the community are doing, and what great tools are out there?"

Student: "Let's start with Anchor. I keep hearing it's the go-to for on-chain program development on Solana?"

Teacher: "Exactly! Anchor is a development framework for Solana Rust programs. It offers account validation, serialization, IDL, a testing framework, and an entire suite that dramatically reduces cognitive load. With Anchor, you can describe program interfaces more clearly, auto-generate clients, and write tests with ease. If you're building on-chain programs, Anchor should be your first choice."

Student: "What if I want to build a frontend website that interacts with a contract, what should I use?"

Teacher: "That's where solana/web3.js comes in. It's the most widely used SDK for browsers and Node.js, tightly integrated with wallet ecosystems like Phantom. Create, sign, and send transactions; subscribe to events, it's your end-to-end frontend solution."

Student: "I also want to snoop, uh, I mean query, on-chain data. What should I use?"

Teacher: "That's solana-py. It's the mainstream Python SDK, great for ops scripts, data pipelines, offline tasks. You can also send transactions and query accounts, or run batch jobs. It integrates nicely with the data science toolchain. If you want to wrangle blockchain data in pandas, Python will make it a breeze. Of course, I recommend pxsol even more, it's a SDK crafted by this book's author, tailored for Pythonistas."

Student: "Sounds like each has its role."

Teacher: "There are also various explorers and RPC services: when you need to confirm transactions and logs quickly or debug issues, they're indispensable."

Student: "There are so many tools! I'm afraid they'll be hard to learn."

Teacher: "Remember: the value of tools isn't in mastering every feature, but in knowing which one to use when you need to solve a problem."

The student raised a fist with a tiny cheer.

Student: "Thank you, Teacher!"

Teacher: "Go build something interesting. Next class, you'll do the demo."
