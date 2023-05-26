# EvilProxy
A proxy server that blocks access to websites using blacklisting and content filtering.

# Techniques:

The evil proxy server blocks a web request to websites using two techniques: Blacklisting and Content Filtering:

1. Blacklisting:
   - Blacklisting involves maintaining a list of specific URLs or domains that are explicitly blocked.
   - Pros:
     - Specific blocking: Blacklisting allows you to target specific URLs or domains that are known to be malicious, inappropriate, or unwanted.
     - Easy maintenance: Adding or removing URLs from the blacklist is relatively straightforward, making it easier to manage.
   - Cons:
     - IP vulnurability: Blacklisting typically operates at the domain or URL level rather than the IP address level. When a user tries to access a website using an IP address directly, the request is still routed to the server associated with that IP address, bypassing DNS resolution and domain-based blacklisting.
     - Reactive approach: Blacklisting relies on maintaining an up-to-date list of blocked URLs, which means new or previously unknown malicious URLs may still be accessible until they are added to the blacklist.
     - Resource-intensive: As the blacklist grows, the proxy server needs to constantly compare requested URLs against the list, which can consume system resources.


2. Content Filtering:
   - Content filtering involves examining the content of a webpage or resource to determine whether it should be allowed or blocked based on specific criteria.
   - Pros:
     - Granular control: Content filtering allows you to define specific rules or criteria for blocking URLs based on keywords, categories, or patterns. 
     - Flexibility: You can customize content filtering to meet your specific requirements, such as blocking inappropriate content, malware, or specific types of websites.
   - Cons:
     - False positives: Content filtering may occasionally block legitimate content that matches the defined criteria, leading to false positives.
     - Overhead: Implementing content filtering can introduce additional processing overhead on the proxy server, potentially impacting performance.


# Usage

1. Insert the hostnames you would like to block (if exists) to the blacklists.txt file. (For example, stackoverflow.com)
2. Insert the keywords you would like to block (if exists) to the keywords.txt file. (For example, stackoverflow)
3. Start the proxy server:
    ```
    cd evil_proxy
    python3 main.py
    ```
4. Make a web request (for example, using curl):
    ```
    curl --proxy localhost:8888 http://en.wikipedia.org/wiki/Stack_Overflow
    ```
    This request will be blocked, since the keyword stackoverflow can be found in the webpage parsed HTML.
    ```
    curl --proxy localhost:8888 http:/stackoverflow.com
    ```
    This request will be blocked, since the hostname stackoverflow.com can be found in blacklist file.

    

