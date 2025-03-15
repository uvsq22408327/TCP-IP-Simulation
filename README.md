# TCP-IP-Simulation
Le projet consiste à simuler un échange des paquets de bout en bout entre un client et
un serveur. Le client ouvre la connexion, le serveur le renvoie le nombre demandé de
paquets par le client, ce dernier fermera la connexion dès réception des paquets. Afin
de réaliser ce scénario, il est recommandé de suivre les étapes suivantes : 
Étape 1 (ouverture d’une 
connexion): 
- Le Client envoie un paquet de synchronisation (SYN) au serveur et déclenche
un
temporisateur (TimeOut). 
- Le serveur le renvoie un paquet de synchronisation plus un acquittement (SYN +
ACK). 
Étape 2 (Transfert des données)
- Le client demande au serveur de lui envoyer un nombre variable de paquets (N),
en
précisant sa capacité de réception (taille de sa file d’attente rcvwindow). 
- Le serveur compare N et rcvwindow afin de faire un ou plusieurs envois
- Le client acquitte les paquets soit positivement ou négativement. En cas d’un
acquittement négatif, le serveur retransmettra le ou les paquets erroné(s).
Étape 3 (Fermeture d’une connexion) 
- Le client demande au serveur de fermer la connexion dans un paquet (FIN)
- Le serveur acquitte le paquet (FIN) avec un paquet (en cours de fermeture)
- Le client acquitte le paquet (en cours de fermeture) et déclenche un temporisateur
de
30 seconde puis ferme la connexion. 
Organisation du travail
- Un groupe de 2 étudiants.
- La programmation reste au choix de chaque groupe
- La gestion de certains paramètres est à votre choix (taille de la file, Time Out ,
etc…) Une interface graphique sera appréciée (en option)
