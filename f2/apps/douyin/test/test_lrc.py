from f2.apps.douyin.utils import json_2_lrc


def test_gen_lrc_from_json():
    data = [
        {"text": "CB on the beat,ho", "timeId": "5.700"},
        {"text": "Wasted CTA lovees wasted", "timeId": "10.210"},
        {"text": "Wasted I'm on these drugsI feel wasted", "timeId": "12.760"},
        {"text": "Wasted get her off my mind when I'm wasted", "timeId": "15.350"},
        {"text": "Wasted I'm waste all my time when I'm wasted", "timeId": "17.740"},
        {"text": "Wasted CTA lovees wasted", "timeId": "20.790"},
        {"text": "Wasted I'm on these drugsI feel wasted", "timeId": "22.900"},
        {"text": "Wasted get her off my mind when I'm wasted", "timeId": "25.850"},
        {"text": "Wasted I'm waste all my time when I'm wasted", "timeId": "28.210"},
        {"text": "Wasted", "timeId": "30.830"},
        {"text": "Damn why is she so demonic", "timeId": "31.320"},
        {"text": "She medusa with a little pocahontas", "timeId": "33.510"},
        {"text": "She been lacin all my drugs or sosomethin", "timeId": "36.150"},
        {
            "text": "Cause every time that we're together I'm unconscious",
            "timeId": "38.560",
        },
        {"text": "Hold upuhlet me be honest", "timeId": "41.100"},
        {"text": "I know l saw her put the percs in my chronic", "timeId": "43.760"},
        {"text": "Smokintil my eyes roll back like the omen", "timeId": "46.370"},
        {"text": "Just another funeral for hergod damn", "timeId": "48.370"},
        {"text": "Wasted CTA lovees wasted", "timeId": "61.320"},
        {"text": "Wasted I'm on these drugsI feel wasted", "timeId": "63.890"},
        {"text": "Wasted get her off my mind when I'm wasted", "timeId": "66.400"},
        {"text": "Wasted I'm waste all my time when I'm wasted", "timeId": "68.970"},
        {"text": "Wasted", "timeId": "71.160"},
        {"text": "She do cocaine in my basement", "timeId": "72.170"},
        {"text": "I'm a doctorsbut I'm runninout of patience", "timeId": "74.270"},
        {"text": "She told me that she tryna get closer to satan", "timeId": "76.760"},
        {"text": "She be talkin to him when she in the matrix", "timeId": "79.450"},
        {
            "text": "Rockstarthat's our stylethere boys can't take it",
            "timeId": "81.770",
        },
        {"text": "Hatin but they're still tryna take our cadence", "timeId": "83.930"},
        {"text": "No basicbrand new rari when I'm racin", "timeId": "86.870"},
        {
            "text": "Take itlet you roll my weedplease don't lace ityeah",
            "timeId": "89.340",
        },
        {"text": "That's a bum that you chasinayy", "timeId": "92.330"},
        {"text": "Foreign with meshe a dominatrix", "timeId": "95.220"},
        {"text": "I love that girls and I do like her body", "timeId": "97.270"},
        {"text": "I don't what the moneyI just want the molly", "timeId": "98.820"},
        {
            "text": "That's what she say when she livesd in the valley",
            "timeId": "100.160",
        },
        {"text": "Lil boyI'm your fatherhakuna matata", "timeId": "101.380"},
        {"text": "I made that girl girls all of that top up", "timeId": "102.220"},
        {
            "text": "Got dreadrs in my headused to pray for the lock up",
            "timeId": "103.360",
        },
        {
            "text": "I htit from the back and my legs start to lock up",
            "timeId": "104.850",
        },
        {"text": "Jacuzzi thar bootyI gave that girl flakka", "timeId": "106.540"},
        {"text": "I'm talkinblue caps that keep tweakinmy chakra", "timeId": "107.520"},
        {"text": "Rose on my chainthere's no hint like no copper", "timeId": "108.860"},
        {"text": "Take in the middle my head like I'm avatar", "timeId": "110.190"},
        {"text": "That's the reason that I ride on my appas", "timeId": "111.510"},
        {"text": "Wasted", "timeId": "112.710"},
        {"text": "WastedGTA lovees wasted", "timeId": "122.290"},
        {"text": "WastedI'm on these drugsI feel wasted", "timeId": "124.800"},
        {"text": "Wastedget her off my mind when I'm wasted", "timeId": "127.380"},
        {"text": "WastedI waste all my time when I'm wasted", "timeId": "130.120"},
        {"text": "My eyes closedhopinthis ain't makebelieve", "timeId": "132.850"},
        {
            "text": "And she don't know hate all her demons like in me",
            "timeId": "135.150",
        },
        {"text": "L don't know l don't know", "timeId": "137.730"},
        {"text": "Don't know what she been onI don't know", "timeId": "143.870"},
        {"text": "All that lean l ain't have to let her in", "timeId": "146.470"},
        {
            "text": "She ain't take my heart,but she took my medicine",
            "timeId": "148.580",
        },
        {"text": "Least somebody gon'take lthate to waste it", "timeId": "151.330"},
        {"text": "WastedGTA lovees wasted", "timeId": "152.980"},
        {"text": "WastedI'm on these drugsI feel wasted", "timeId": "155.610"},
        {"text": "Wastedget her off my mind when I'm wasted", "timeId": "158.070"},
        {"text": "WastedI waste all my time when I'm wasted", "timeId": "160.820"},
    ]

    print(json_2_lrc(data))


if __name__ == "__main__":
    test_gen_lrc_from_json()
