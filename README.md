# KDS

Final project for our Communication and Distributed Systems labs. In it, we will implement the Selective Repeat algorithm. Our code code consists of server class which sends given file (any file format) and a client class which recieves and also saves the file from server. To ensure that the file was correctly transmitted, we compute and send hash(sha256) on the server-side and send it to client along side the file itsels. Once received on the client-side, the client computes the hash of the received file and checks whether it matches the hash sent from server\n

For more indormation, see the diagram below:

![Your SVG Diagram](./diagrams/server-client.svg)

