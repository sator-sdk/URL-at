# URL@

Python script that craft links with embedded @ sign for redirection to an obfuscated address

Read the Blog [post](https://sator-sdk.github.io/posts/url-at-redir/) in oder to give some context.

## URL Redirect Schema Abuse: The Stealthy Exploits of the @ Sign

URL redirect schema abuse is a prevalent and evolving cyber threat that exploits the intricacies of web protocols to deceive users and manipulate their online experiences. One increasingly popular technique involves the misuse of the `@` sign within URLs to redirect users to unintended destinations, and also the use of additional techniques that expand the redirection trick. This article aims to shed light on this deceptive practice, examining its mechanics, potential consequences, and strategies for mitigation.
What I'm going to describe here it's also very well described from two major articles by [Mandiant](https://www.mandiant.com/resources/blog/url-obfuscation-schema-abuse) and [RedCanary](https://redcanary.com/blog/google-zip-domains/).

### Craft those links

So when we actually want to try them out in our red team or phishing engagements to be able to replicate them the obvious way is to craft those link by yourself but ther are some handy tools out there that could help you with that. I developed a Python script that automate all that procedure, and i used it occasionally during assessments, the core of the translation of an IPv4 structure to the other notation formats was inspired from a tool by Vincent Yiu [IPFuscator](https://github.com/vysecurity/IPFuscator) that its a bit outdated by now and still in python2, so i decided to give it a modern look and add some interesing features to ease of use and craft redirection link in seconds.

### DISCLAIMER

> The script is for demonstration purposes only! The misuse of that script for illicit purposes is at your own risk, should be used only in legitimate penetration test assignments with explicit permission.

---

### Description

Is a comamnd line utility tool that automatically generation of those kind of links in multiple ways, by providing some command line arguments:

* `-i`: Redirect Destination IP to perform mutation on

Or if preferred the IP could be directly retrieved from DNS records of an existing server with `-d`

* `-s`: Domain name URL that act as legit domain

* `-p`: Redirect Destination URL path (optional) is the ending path of the file on final server

* `-sp`: URL arguments after the TLD of the "-s" specified domain to perform encoding on. This field could also be included in the `-s` argument but will only be encoded if passed via `-sp` not `-s` even though the unicode char substituion is performed in all the passed fields except from `-p` that should NOT be modified with fake slash encoding

* `-r`: Generate random URL schema. Obfuscating links inside code that should appear not pointing to a searchable domain. I have observed inside some malware samples only the goal of trick the scanning software as long as they can to avoid detection of hardcoded link that will possibly lead to a CnC infrastructure discovery.

* `-f`: Replace slashes in schema or schema-path with unicode char U+2215

* `-e`: Encode the final URL - the argument of the `-sp` parameter is base64 encoded while the rest is url encoded


<p align="center">
<img src="/pics/urlathelp.png">
</p>
<p align="center">
Help menu
</p>

### Set the `/` separator to the unicode `2215`

```shell
# unicode 2215
python urlat.py -i 192.168.1.119 -s 'totally.legit.domain.tld/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' -f
```
<p align="center">
<img src="/pics/unicode2155.png">
</p>
<p align="center">
unicode 2215 by default url-encoded if not passed through the -sp tag
</p>

#### `-sp` tag

```shell
# Unencoded unicode 2215 in the encodable variable
python urlat.py -i 192.168.1.119 -s totally.legit.domain.tld -sp '/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' -f
# Encoded links with unicode char 2215
python urlat.py -i 192.168.1.119 -s totally.legit.domain.tld -sp '/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' -e -f
```
<p align="center">
<img src="/pics/userpathunicode.png">
</p>
<p align="center">
unicode 2215 here shown not encoded
</p>

### Add the final redirection path

```shell
python urlat.py -i 192.168.1.119 -s totally.legit.domain.tld -sp '/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' \
-e -f -p /api/v1/file.zip
```

<p align="center">
<img src="/pics/redirpath.png">
</p>
<p align="center">
Redirection path
</p>

### Base64 Example

In that example you could craft base64 encoded links that actually even without the `/` set to the unicode `2215` value will redirect the page.

> **IMPORTANT**: As mentioned in the blog post important to use when possible the mixed creafted dotted-quad notation in order to perform a flawless redirect.

In the script only the path of the legit domain (the User-Info path) is encoded to mimic some known behaviour of popular url rewrite mechanisms that encode only some data in that part and not in others, actually to base64 encode only specific values of some parameters would be even better for tricking an expert user, and i suggest to do it manually, or maybe i will add a functionality in the script, but for now a obfuscation of the whole path parameter is fine.
Also i hardcoded some values that improve the whole mechainism and are needed in some situations, like the `%20` after the TLD of the legit domain or the `%7F` before the `@`, but keep in mind that you would prefer to swap those values or even add as many as you want for each link you could use in order to not increment fingerprinting.

```shell
# fictional domain and parameters
python urlat.py -i 192.168.1.119 -s totally.legit.domain.tld -sp '/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' -e
```

<p align="center">
<img src="/pics/urlatlinks.png">
</p>
<p align="center">
Base64 encoded links
</p>

### Retrieve Domain from DNS records

```shell
# fictional domain and parameters
python urlat.py -d my.custom.c2.domain.com -s totally.legit.domain.tld -sp '/api/v1/signin/ident?klmer=G1927123976%3A893513460&redir=https%3A%2F%2Fanother.domain&Loing&dobui=b253cnZqbmRzd3JvdmJ3cm92amJvd3dka2piZHZvZWlqY2V3b2lubm9rbmN3d29u' -e
```

### Random URL

The format is actually inspired from source code of AgentTesla sample that store links in that format to avoid detection. Keep in mind that it doesn't have to be considered an obfuscation method the one that is used it only provide a less enthropy 64 char long link padded with zeroes and following some paricualar random rules when generating the letters in order to provide less enthropy to the file it will be embeeded in.

```shell
python urlat.py -i 192.168.1.119 -r
```
<p align="center">
<img src="/pics/randomlinks.png">
</p>
<p align="center">
Random links
</p>
