## TASKS

What about duplicates when importing TMX segments? -> will not be added to DB 
Do we need to recreate original sequence of TMX => Yes may want to do this
Versioning -> use toimestamp then get latest timestamp version

Remove Units from TMXFile only need ID in each segment
Add domainInfo to segment !!!
Create DOmain objects


HOW?

POSTGRES
1 setup 2 tables for TMXFile and Segments
2 write to File
3 write to Segment (best as go along not at end)

1:n
TMXFile 1 has n segments
Segment has only 1 TMXFILE

Prio once we have some files in DB -> 
writeTMX routine

getTMX UUID

Start with One User ADMIN

getLatestSegments UUID 
assignSegmentsToWorker (FileUUID)
getLatestSegmentsForWorker 

Can also slice up based on difficulty 
 


CreateTMX endpoint 
based on JSON criteria?

Input source file -> get translation from Yandex/ChatGBT -> write to file return as Product for use in tools!

Any source Format -> [HUMANINLOOP] => translation ->> [POSTEDIT of TRANSLATION HumaninLoop ]


Payment is by UUID of document + service + target

API
Create Service table



HumanInLoop FrontEnd is 1 page for TMXUpload XLIFF upload return as TMX
TXT SRT etc as TMX
LATER Auto Assign to worker
Plus BackEnd emil login sees




payment page is UUID document -> make payment via crypto or paypal as reference





## EXAMPLE PUTPIT

        Segment(
            fromFileId=UUID('6fdca46c-7c50-4c84-a1f0-0e7b3e631b77'),
            segId=UUID('63c9eb79-e39c-4c18-9172-a839a82ae00a'),
            seqNo=34314,
            srcLang=<AcceptedLanguage.deDE: 'de-de'>,
            trgLang=<AcceptedLanguage.enUS: 'en-us'>,
            srcText='Abstimmung Fahrverhalten Hydraulisches Hinterachslager',
            cleanSrcText='Abstimmung Fahrverhalten Hydraulisches Hinterachslager',
            trgText='Coordination of handling characteristics of hydraulic rear axle bearing',
            cleanTrgText='Coordination of handling characteristics of hydraulic rear axle bearing',
            segNote='',
            srcWordCount=4,
            timestamp='2023-06-08 16:25:30'
        ),
        Segment(
            fromFileId=UUID('6fdca46c-7c50-4c84-a1f0-0e7b3e631b77'),
            segId=UUID('c5145066-4181-4472-96eb-c5b3b6bc7aac'),
            seqNo=34315,
            srcLang=<AcceptedLanguage.deDE: 'de-de'>,
            trgLang=<AcceptedLanguage.enUS: 'en-us'>,
            srcText='Umrüstung Connected unlimited',
            cleanSrcText='Umrüstung Connected unlimited',
            trgText='Conversion of Connected unlimited',
            cleanTrgText='Conversion of Connected unlimited',
            segNote='',
            srcWordCount=3,
            timestamp='2023-06-08 16:25:30'
        )
    ],
    srcWordCount=235983,
    totalSegs=34315
)


# refs

https://fastapi.tiangolo.com/tutorial/query-params/