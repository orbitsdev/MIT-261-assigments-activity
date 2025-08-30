# MIT 261 – Session 2: Interactive Student Class List in a Distributed MongoDB System

## Laboratory Description

This laboratory activity introduces students to the integration of MongoDB Atlas with a Flask web application. Students will explore the principles of distributed database systems, focusing on high availability, secure connections, and resilient query operations. By designing and executing aggregation pipelines, learners will transform raw academic datasets into meaningful insights about students, subjects, teachers, and semester enrollment. The activity also emphasizes hands-on analytics by building interactive dashboards that allow dynamic filtering, exploration, and performance evaluation of distributed education data.

## Laboratory Objectives

1. To demonstrate secure connection to a MongoDB Atlas cluster using environment variables and high availability settings.
2. To configure ReadPreference, ReadConcern, and Write Concern for resilient operations in a distributed system.
3. To design aggregation pipelines that:
   - Unwind array fields (e.g. SubjectCodes, Grades, Teachers)
   - Join data across multiple collections (grades, students, semesters, and subjects)
   - Sort results for meaningful reporting (e.g. alphabetically by student name)
4. To implement web-based interactive filters for exploring MongoDB datasets.
5. To apply best practices for real-time performance analytics in educational datasets.

## Learning Outcomes

By the end of the laboratory, students will be able to:

1. Connect securely to a MongoDB Atlas cluster with high availability settings.
2. Explain the role of ReadPreference, ReadConcern, and WriteConcern in ensuring data reliability in distributed systems.
3. Construct and execute complex aggregation pipelines that perform operations such as filtering, grouping, sorting, and joining collections.
4. Develop interactive web interfaces that allow real-time exploration of student and subject data.
5. Interpret MongoDB query results to analyze GPA patterns, identify high and low performing students, evaluate subject-level GPA averages and provide actionable academic performance insights.
6. Evaluate system resilience by analyzing how read and write configurations affect query outcomes during replica set failover.

## Implementation Details

### MongoDB Connection

The application connects to MongoDB Atlas using a secure connection string stored in the configuration file. The connection includes:
- Retry mechanisms for better resilience
- Read preference settings for distributed load
- Connection pooling for better performance

### Aggregation Pipeline

The implementation uses a two-phase aggregation approach:
1. First phase: Early filtering and ID collection with pagination
2. Second phase: Detailed data retrieval with lookups across collections

Key optimizations include:
- Early $match filtering to reduce memory usage
- Strategic unwinding of arrays
- Proper indexing for faster lookups
- Caching with TTL for frequently accessed data

### User Interface

The web interface provides:
- Subject and semester filters
- Class statistics (GPA, enrollment counts)
- Pagination controls
- Loading indicators for better UX
- Responsive design with Tailwind CSS

### Performance Optimizations

- In-memory caching with TTL expiration
- Two-phase aggregation to reduce memory usage
- Batch size optimization for cursor handling
- Timeout settings to prevent long-running queries
- Indexes on frequently queried fields

## Sample Output

The application displays a class list with:
- Student information (ID, name, course, year level)
- Subject details (code, description, units)
- Teacher assignment
- Grades
- Semester information
- Class statistics (GPA, students above/below GPA)

## MongoDB Schema

The application works with the following collections:
- grades: Contains student grades with references to subjects, teachers, and semesters
- students: Student information including name, course, and year level
- subjects: Subject details including code, description, and units
- semesters: Semester information including term and school year
