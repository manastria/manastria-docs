# Configuration d'un serveur DHCP multi-VLAN avec relais DHCP : Une approche pratique

## Introduction

Dans un réseau d'entreprise moderne, la gestion manuelle des adresses IP devient rapidement complexe et source d'erreurs. Imaginez devoir configurer individuellement les paramètres réseau de centaines d'ordinateurs ! C'est là qu'intervient le protocole DHCP (*Dynamic Host Configuration Protocol*), qui automatise cette tâche essentielle.

Cette activité pratique vous guidera à travers la mise en place d'une infrastructure DHCP dans un environnement réseau segmenté. Vous allez progressivement construire une solution complète, en partant d'une configuration simple pour arriver à une architecture plus sophistiquée avec plusieurs VLANs.

## Contexte et objectifs pédagogiques

Imaginons une petite entreprise qui souhaite séparer son réseau en deux segments distincts :

- Un VLAN 10 pour les services informatiques (où sera notre serveur DHCP)
- Un VLAN 20 pour les postes des employés

Cette séparation pose un défi intéressant : comment permettre aux ordinateurs du VLAN 20 d'obtenir automatiquement leurs configurations réseau alors que le serveur DHCP se trouve dans un autre VLAN ? C'est là que la notion de relais DHCP prend tout son sens.

## Phase 1 : Configuration de base - Le DHCP dans un environnement simple

### Matériel nécessaire

- 1 switch Cisco 2960 (ou similaire)
- 1 PC physique pour héberger la machine virtuelle serveur Debian 12
- 1 PC client (physique ou virtuel, différent du PC serveur)
- Câbles réseau droits

### Synoptique de l'infrastructure

![Synoptique de l'infrastructure](./images/Réseau E1.drawio.svg)

### Mise en place de l'infrastructure initiale

1. **Configuration du PC serveur**
    1. Installez VirtualBox ou VMware sur votre PC physique
    2. Créez une machine virtuelle Debian 12 avec une interface réseau en mode Bridge
    3. Configurez l'adresse IP statique sur la VM Debian :
        1. Adresse IP : 192.168.1.10
        2. Masque : 255.255.255.0
        3. Passerelle : pour l'instant, pas nécessaire
2. **Configuration du switch**
    1. Pour cette première phase, aucune configuration n'est nécessaire
    2. Laissez le switch dans sa configuration par défaut (tous les ports en VLAN 1)
    3. Connectez :
        1. Le PC physique hébergeant la VM serveur sur le port Fa0/1
        2. Le PC client sur le port Fa0/2
3. **Installation et configuration du serveur DHCP**
    1. Utilisez votre fiche technique pour installer le package `isc-dhcp-server`
    2. Configurez le serveur DHCP avec les paramètres suivants :
        1. Plage d'adresses : `192.168.1.100` à `192.168.1.200`
        2. Masque de sous-réseau : `255.255.255.0`
        3. Passerelle : `192.168.1.1` (pour plus tard)
        4. Serveur DNS : `8.8.8.8`

### Tests de validation

Pour vérifier que votre configuration fonctionne correctement, suivez cette procédure de test pas à pas :

1. **Sur le serveur Debian**

```
# Vérifiez que le service DHCP est actif
sudo systemctl status isc-dhcp-server

# Vérifiez les logs DHCP pour d'éventuelles erreurs
sudo tail -f /var/log/syslog | grep dhcp
```

➜ Le service doit être "active (running)"

➜ Les logs ne doivent pas montrer d'erreurs

1. **Sur le PC client**
    1. Windows :
    ```
    ipconfig /release
    ipconfig /renew
    ipconfig /all
    ```

    2. Linux :
    ```
    sudo dhclient -r
    sudo dhclient
    ip a
    ```

    ➜ Vous devez observer :

    1. Une adresse IP dans la plage `192.168.1.100-200`
        1. Le masque `255.255.255.0`
        2. La passerelle `192.168.1.1`
        3. Le serveur DNS `8.8.8.8`
    2. **Tests de connectivité**
    ```
    # Depuis le client
    ping 192.168.1.10  # Vers le serveur DHCP

    # Depuis le serveur
    ping [IP_obtenue_par_le_client]
    ```

    ➜ Les pings doivent fonctionner dans les deux sens

2. **Vérification des baux DHCP**

```
# Sur le serveur
cat /var/lib/dhcp/dhcpd.leases
```

➜ Vous devez voir l'adresse MAC de votre client et l'IP qui lui a été attribuée

### Résolution des problèmes courants

- Si le service ne démarre pas : vérifiez les logs avec `journalctl -xe`
- Si le client n'obtient pas d'adresse :
    - Vérifiez la connexion physique (LEDs du switch)
    - Assurez-vous que le pare-feu du serveur autorise DHCP
    - Contrôlez que l'interface réseau est correctement déclarée dans `/etc/default/isc-dhcp-server`

## Phase 2 : Mise en place de la segmentation réseau avec Router-on-a-stick

Maintenant que notre serveur DHCP fonctionne dans un réseau simple, nous allons créer une infrastructure plus sophistiquée avec deux VLANs distincts. Cette configuration reflète mieux la réalité d'une entreprise où différents services doivent être séparés logiquement.

### Matériel supplémentaire nécessaire

- 1 routeur Cisco 2901 (ou similaire)
- 1 câble console pour la configuration du routeur
- 1 câble réseau supplémentaire pour connecter le switch au routeur
- Configurer la connexion SSH sur le routeur et le switch

### Nouvelle architecture réseau

Pour cette phase, nous allons créer :

- VLAN 10 (Service informatique) : réseau `192.168.10.0/24`
- VLAN 20 (Employés) : réseau `192.168.20.0/24`


#### Topologie physique
![Topologie physique](./images/Réseau E2.drawio.svg)


#### Topologie logique
![Topologie logique](./images/Réseau E3.drawio.svg)


### Étapes de configuration

1. **Préparation du switch**
    1. Connectez-vous au switch via le câble console
    2. Créez les VLANs selon les paramètres suivants :
        1. VLAN 10 : « INFORMATIQUE »
        2. VLAN 20 : « EMPLOYES »
    3. Configurez les ports :
        1. Fa0/1 : mode trunk (vers le routeur), il est préférable d’utiliser un port gigabit du switch
        2. Fa0/2 : VLAN 10 (serveur DHCP)
        3. Fa0/3 : VLAN 20 (client)
2. **Configuration du routeur**
    1. Connectez le routeur au port Fa0/1 du switch
    2. Créez les sous-interfaces pour chaque VLAN :
        1. G0/0.10 : `192.168.10.1/24` (passerelle VLAN 10)
        2. G0/0.20 : `192.168.20.1/24` (passerelle VLAN 20)
3. **Modification du serveur DHCP**
    1. Modifiez l'adresse IP de la VM Debian :
        1. Nouvelle IP : `192.168.10.10/24`
        2. Passerelle : `192.168.10.1`
    2. Ajustez la configuration DHCP pour le VLAN 10 :
        1. Plage : `192.168.10.100` à `192.168.10.200`
        2. Passerelle : `192.168.10.1`
        3. DNS : `8.8.8.8`

### Tests de validation étape par étape

1. **Vérification des VLANs**

    ```
    # Sur le switch
    show vlan brief
    ```

    ➜ Vérifiez que :

    1. Les VLANs 10 et 20 sont créés
        1. Fa0/2 est bien dans VLAN 10
        2. Fa0/3 est bien dans VLAN 20
    2. **Vérification du trunk**

    ```
    # Sur le switch
    show interfaces trunk
    ```

    ➜ Le port Fa0/1 doit apparaître comme trunk

2. **Test des sous-interfaces du routeur**

    ```
    # Sur le routeur
    show ip interface brief
    ```

    ➜ Vérifiez que :

    1. G0/0.10 est "up/up" avec IP 192.168.10.1
    1. G0/0.20 est "up/up" avec IP 192.168.20.1

3. **Test depuis le serveur DHCP**

    ```
    # Sur la VM Debian
    ip a                    # Vérifier la nouvelle IP
    ping 192.168.10.1       # Tester la connectivité avec la passerelle
    ```

    ➜ Les pings vers la passerelle doivent fonctionner

4. **Test depuis le client** Pour ce test initial, configurez une IP statique sur le client :
    1. IP : `192.168.20.100`
    2. Masque : `255.255.255.0`
    3. Passerelle : `192.168.20.1`

    Puis testez :

    ```
    ping 192.168.20.1       # Passerelle VLAN 20
    ping 192.168.10.1       # Passerelle VLAN 10
    ping 192.168.10.10      # Serveur DHCP
    ```

    ➜ Tous les pings doivent fonctionner

### Résolution des problèmes courants

- Si les pings entre VLANs ne fonctionnent pas :
    - Vérifiez que `ip routing` est activé sur le routeur
    - Contrôlez l'encapsulation dot1Q sur les sous-interfaces
    - Assurez-vous que les VLANs sont bien créés sur le switch
- Si le serveur DHCP n'est plus accessible :
    - Vérifiez que son adresse IP a bien été changée pour `192.168.10.10`
    - Contrôlez que le port du switch est dans le bon VLAN
    - Testez la connectivité avec la passerelle

À ce stade, nous avons :

- Deux réseaux logiquement séparés
- Un routage fonctionnel entre les VLANs
- Mais le DHCP ne fonctionne que dans le VLAN 10

La prochaine étape sera de permettre aux clients du VLAN 20 d'obtenir automatiquement leurs paramètres réseau via le relais DHCP.

## Phase 3 : Mise en place du relais DHCP

À ce stade, notre réseau est segmenté en deux VLANs distincts, mais nous faisons face à un défi intéressant : comment permettre aux postes du VLAN 20 d'obtenir automatiquement leurs configurations réseau alors que le serveur DHCP se trouve dans le VLAN 10 ?

Pour comprendre l'importance du relais DHCP, imaginons une situation réelle : vous avez deux bureaux séparés par un couloir. Le serveur DHCP est dans le bureau des informaticiens (VLAN 10), mais les employés dans l'autre bureau (VLAN 20) ont aussi besoin d'obtenir leurs configurations réseau. Le relais DHCP agit comme un messager qui va transmettre les demandes d'un bureau à l'autre.

### Configuration du relais DHCP

1. **Configuration du routeur comme relais**
    1. Connectez-vous au routeur via le câble console
    2. Sur l'interface du VLAN 20, configurer le relais DHCP (`ip helper-address`)
2. **Adaptation du serveur DHCP pour le VLAN 20**
    1. Sur la VM Debian, modifiez le fichier /etc/dhcp/dhcpd.conf
    2. Ajoutez une nouvelle déclaration de sous-réseau pour le VLAN 20
    3. Redémarrez le service DHCP :

    ```
    sudo systemctl restart isc-dhcp-server
    ```

### Tests approfondis

1. **Vérification de la configuration du relais**
```
# Sur le routeur
show running-config interface g0/0.20
```

➜ Vérifiez que la commande `ip helper-address 192.168.10.10` apparaît

2. **Observation du processus DHCP en temps réel**
```
# Sur le routeur
debug ip dhcp server packet
debug ip dhcp relay
```

Ces commandes vous permettront d'observer les échanges DHCP en direct.

1. **Test sur le PC client**
    1. Configurez l'interface réseau en DHCP automatique
    2. Sur Windows :

    ```
    ipconfig /release
    ipconfig /renew
    ipconfig /all
    ```

2. Sur Linux :
    ```
    sudo dhclient -r
    sudo dhclient
    ip a
    ```

    ➜ Vérifiez que :

    1. L'adresse IP obtenue est dans la plage `192.168.20.100-200`
        1. La passerelle est `192.168.20.1`
        2. Le serveur DNS est `8.8.8.8`
    2. **Tests de connectivité complète** Depuis le PC client :

    ```
    ping 192.168.20.1       # Passerelle locale
    ping 192.168.10.1       # Passerelle distante
    ping 192.168.10.10      # Serveur DHCP
    ```

   Tous ces pings doivent fonctionner.

3. **Vérification des baux DHCP** Sur le serveur Debian :

    ```
    cat /var/lib/dhcp/dhcpd.leases
    ```

    ➜ Vous devriez voir des baux pour des adresses dans les deux plages (VLAN 10 et 20)

### Comprendre ce qui se passe

Quand un client du VLAN 20 demande une adresse IP :

1. Il envoie une requête DHCP en broadcast
2. Le routeur reçoit cette requête sur G0/0.20
3. Grâce à `ip helper-address`, il la transmet en unicast au serveur DHCP
4. Le serveur répond avec les paramètres du VLAN 20
5. Le routeur retransmet la réponse au client

### Résolution des problèmes courants

Si le client n'obtient pas d'adresse :

1. Vérifiez les logs sur le serveur DHCP :
    ```
    tail -f /var/log/syslog | grep dhcp
    ```

2. Sur le routeur, confirmez que les requêtes sont relayées :
    ```
    show ip dhcp relay statistics
    ```

3. Points à vérifier :
    1. La déclaration du sous-réseau 192.168.20.0 dans dhcpd.conf
    2. La configuration du relais sur la bonne sous-interface
    3. L'accessibilité du serveur DHCP depuis le routeur

Cette configuration complète permet maintenant à tous les clients, quel que soit leur VLAN, d'obtenir automatiquement leur configuration réseau de manière sécurisée et organisée.
