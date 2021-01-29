
# MTG Card Scanner
This is a project that I am currently working on that can be used to identify Magic: The Gathering cards using a camera. The indented use of this program is to make exporting large lists of cards quicker and easier by not requiring you to manually type in the name of every card.

## Card Scraper
The card scraper portion of this program creates hashed image fingerprints for all cards found on [The Gatherer](https://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[%22%22]), Wizards of the Coast's official MTG card database. The images that appear on The Gatherer are collected, cropped to include only each card's art, and converted to a 64-bit fingerprint using a "difference hash" (dHash) of the image. These fingerprints are then stored in a local json file to be searched for by the card scanner.

## Card Scanner
To scan a card, first the image pulled from the webcam must be cropped down to just the area that contains the card. This is done by converting the image to a greyscale image, blurring the image slightly, and then using [Canny edge detection](https://docs.opencv.org/master/da/d22/tutorial_py_canny.html) to find borders in the image. Then, these edges are dilated to fill in possible breaks in the edge of the card. Then, a list of complete contours is generated and the largest contour (presumably the region of the image where the card is) is returned.

Once the image has cropped to just the area where the card is, just the card's art is extracted, and a dHash is performed on it. The resultant fingerprint is then compared to all of the scraped fingerprints to find the print with the smallest [hamming distance](https://en.wikipedia.org/wiki/Hamming_distance), which should belong to the correctly identified card being scanned.