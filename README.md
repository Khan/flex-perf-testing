# Google App Engine: Performance Testing

This repo is consists of a collection of tests for determining the latency of various operations and services on Google App Engine Flex and Standard. The goal of these tests was to inform architectural decisions by the Infrastructure team at Khan Academy for determining which services—if any—to migrate to App Engine Flex.

## Context

For the past several years, Khan Academy has hosted its backend on Google App Engine Standard. App Engine has served us quite well, but it has a few limitations:
* Inability to separate services
* Inability to modify the runtime or OS of the machine the backend runs on

Flex on the other hand allows for the above capabilities:
* You can separate your backend into microservices 
* You can input custom images to run the services on
* You can configure memory and CPU settings for each service
* It's faster (?!)

The last point is the question we wanted to investigate with these tests.

## Testing

We tested multiple parts of Google App Engine Flex and Standard:
* Memcache
   * Testing the `set`, `get`, and `delete` operations on the Memcache at various data sizes, as well as testing multithreaded requests
* Datastore/ndb
   * Testing the new Datastore on Flex as well as `db` and `ndb` (the database services on Standard) with the `put`, `get`, and `delete` operations with various payload sizes

We created separate template apps in both Standard and Flex that make the necessary calls to the App Engine API and run a timer on those calls. The deployed apps (see `flex/` and `standard/`) are essentially API endpoints that take an operation and data size as input, complete that operation with random data, and return the time it took for the operation to complete. We collected about 25,000 latency samples for each operation, and analyzed the results by looking at the distribution by percentile for each operation. 

## Results

See this [report](https://paper.dropbox.com/doc/Flex-vs.-Standard-Performance-Tests-cdwSMLIwzde5jzL9P6htN) on Dropbox Paper with the results of the testing, including some graphs and key takeaways. **Note:** these tests were done on an early preview version of Flex ndb, and thus are in no way definitive results on the performance of Flex compared to Standard. They simply provide useful data points for the Khan Academy team as we make architecture choices and continue to survey the land of Google App Engine.