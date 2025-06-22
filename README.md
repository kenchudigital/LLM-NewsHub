# LLM News Generation

## My env
```
Mac M1 Pro - 16GB RAM (CPU only)
Python 3.10.18
package: /requiremensts.txt
```

## Git Intrusction 

> How to modify the code?

1. Create the new branch (eg. dev/{feature_name})
2. After pushed in new branch, then create the `Pull Request`
3. Ask Ken to review the code
4. If approved, then merge to the main branch

When push:

```bash
# if needed (BTW, I have set .gitmodules)
git submodule add https://github.com/Rudrabha/Wav2Lip 
```

## Quick Start - [LINK](/quick_start.md)

## Demo 

![Demo](z-img/demo.gif)

## TODO LIST

Potential Optimize:

Remeber that need to add AI-Generated label for the content.

0. Easy
    - Hot Topics
    - Time Weights (when grouping, use other date data)
    - Score Usage
1. Clustering
    - Instead of Kmeans such as DBSCAN
2. Fake New Classification
    - Add the content pattern as Feature
3. Generation Approach
4. Evaluation Methods
    - Any Metrics Need  
5. Deployment
    - Improve the image prompt for Stable Diffusion
    - Voice Fine Tuning
6. UI
    - Create Top Hot News according to the Social Media data
    - Avatar Chatbot ?
    - Video (Wip2Lip) for Summary of today ?
7. Git
    - Create CODEOWNERS file

FEAT:
- GNN 
    - Search
    - Fact Check
    - Recommendation

[SO DIFFICULT TO HANDLE `GRAPH` IN `JAVASCRIPT` BUT HANDLE IN `PYTHON SCRIPT` NEED TO PROVIDE THE FIXED CONTENT OR CREATE THE `API CALL` FOR THAT]

---

## MIT License  

This project is licensed under the **MIT License**.  
For details, see [LICENSE](/license).  

