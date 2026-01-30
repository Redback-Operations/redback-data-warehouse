# LocalAGI Agent – RedBack Query

> Converted from `LocalAGI Agent RedBack Query.docx`

The following is a proof of concept configuration of a LocalAGI Agent to facilitate the ability to ask questions about the redback onboarding document.


Agent Configuration for Redback Chat


Connect to


Select Agent List

![Image](images/img01.png)


And then Create agent

![Image](images/img02.png)


Complete details as follows


![Image](images/img03.png)


![Image](images/img04.png)


For the API keys use the API key that was created for LocalAI. In the original install it was done as follows:


```bash
openssl rand -hex 32
```


```bash
sk-SOMESECRET
```



![Image](images/img05.png)

This enables the use of localrecall for RAG.


![Image](images/img06.png)


The following shows the Localrecall setup


You can connect to Localrecall via


![Image](images/img07.png)


It is now possible to chat with the agent per the following


![Image](images/img08.png)


![Image](images/img09.png)


