Dev Notes

Rolling todo:
1. you're considering "going bust" the wrong way. because you calculate returns always starting at the beggining, you can't model the going bust risk of investing everything right before a crash. you need to remake your business logic so that you calculate portfolio value starting at the beginning of each window, not at the beginning of all timme. I think you need to call simulate portfolio over each time window-- logic heavy but nessisary. 
