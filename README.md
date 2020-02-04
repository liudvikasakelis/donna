# Donna

Before you is my interpretation and implementation of a stochastic adversarial 
bandit algorithm for **proxy rotation**. A classic use case would be scraping 
the web and getting blocked by the sites' administrators.

Proxy servers help a lot, however, the good ones are not free. There are plenty of free proxy server
lists on the web, but free proxies are unrealiable and slow (in general). *However*, empirically I've found that there's usually a few that perform well, at least for a while. I have no actual facts, but it seems that:

    * both the proxies are blocking us (temporarily, hopefully),
    * and the target sites are blocking the proxies
    * the proxies sometimes just shut down.
    
I think this qualifies the problem to be treated as a case of the adversarial bandit (I'll add a link). 

*Donna*, therefore, is designed to make use of big lists of possibly non-functional proxies. It rates the proxies depending on their performance and prefers the ones with better track record, however it is stochastic, so every proxie will get tested from time to time. I'm cleaning up the module to make it nicer to use, but it's been used in semi-production and is thread-safe as well. 

Help is always appreciated! 
