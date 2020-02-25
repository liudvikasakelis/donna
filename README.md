# Donna

## Quick description

Before you is my interpretation and implementation of a stochastic adversarial 
bandit algorithm for **proxy rotation**. A classic use case would be scraping 
the web and getting blocked by the sites' administrators.

### Usage example

    import donna
    import requests
    pMan = donna.proxyManager('proxy_db.sqlite3')
    pMan.get_proxy()          # this will return the proxy
    # {'http': 'http://0.0.0.0:80', 'https': 'https://1.1.1.1:3128'}

    success_counter = 0
    for url in urls:
        while True:
            request_response = requests.get(url, proxies=pMan.proxy)
            if blocked:
                success_counter = 0
                pMan.finalize(success_counter)
                pMan.get_proxy()
            else:
            success_counter += 1
    
Key takeaways here: 

  * You have to check whether you've been blocked. Maybe comparing the response
  against a known blocked response.
  * Finalizing is not strictly necessary, but the weights don't get updated if
  you don't `pMan.finalize()` with the count of successive successes with that 
  proxy combination. That is to say, you will keep using a known faulty proxy or
  underutilize a known good one. Sometimes this may be desireable.
  * All proxy data are stored in a *sqlite* database. This makes this solution 
  scalable across threads as well as processes (you could have several scrapers 
  using the same database of proxies, updating it at the same time). However, 
  to avoid a possible bottleneck, I've found it very effective to place your 
  database in RAM (on Linux: `/dev/shm`, on Windows - some sort of a RAMdisk).
  
### Proxy database schemas

    CREATE TABLE `http` (
        `ip` TEXT,
        `status` REAL
    )

    CREATE TABLE `https` (
        `ip` TEXT,
        `status` REAL
    )

    INSERT INTO https VALUES (
        '1.2.3.4:8080', 
        100.0
    )

Note that the *ip*  field must include the port, but not the protocol prefix; 
the initial *status* value is not very important, because they're meant to 
change. It should be more than 1. 

## A deeper look

Proxy servers help with scraping a lot, but the good ones are not free. There 
are plenty of free proxy server lists on the web, but free proxies are 
unrealiable and slow (in general). *However*, empirically I've found that 
usually a few perform well (for a while). I haven't been tracking numbers, but 
it seems that:

  * proxies block our IP from time to time, but not always permanently
  * the target site will block the proxy IP, but never permanently
  * the proxies sometimes just shut down - that's quite permanent unfortunately
    
I think this qualifies the problem to be treated as a case of the adversarial 
bandit (I'll add a link). 

*Donna*, therefore, is designed to make use of big lists of possibly 
non-functional proxies. It rates the proxies depending on their performance 
and prefers the ones with better track record, however it is stochastic, so 
every proxy will get tested from time to time. 

Update rule (works OK empirically, but let me know if you discover better rules
): 

    new_status = current_status^0.9 + success_count^0.9 * 10

So, for exapmle, if a proxy is completely useless (fails every single request),
its status will tend to 1. If a proxy gets, on average, one request, and then 
fails, its status should approach

    status^0.9 = status - 10; => status ~ 33
    
Since status values are used as weights for sampling proxies, such
almost-functional proxy will get used 33 times more than the hopeless one. 

The implementation has been used in semi-production and is thread-safe as well. 

Help is always appreciated! 
