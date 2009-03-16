# coding=utf-8

from __future__ import with_statement 
from BeautifulSoup import BeautifulSoup
import urllib2
import PyRSS2Gen
import datetime
import re
import sys

def get_novica_content(soup):
	# \n<h1>TIZLE</h1> ..... <div class="content_footer">...
	contents = soup.find('div', id='content')
#	title = contents.h1.string

	# the content is a bit tricky, cause it's a mixed bag of Tag-s and NavigatableString-s
	# and we want the part from the </h1> to <div class="content_footer">
	real_contents = u""
	start = False
	for child in contents.contents:
		type = getattr(child, "name", None)
		if type == "h1":
			start = True
			continue
		if type == "div" and child['class'] == "content_footer":
			break

		if (start):
			real_contents += unicode(child)
	real_contents = real_contents.strip()
	
	datoteke = find_attachments(soup)
	if (datoteke):
		real_contents += "<p>Datoteke:</p>"
		for datoteka in datoteke:
			real_contents += unicode(datoteka)

	return real_contents

def find_attachments(soup):
	"""
		find attachments, if any
		returns None, or list of soup elements for each attachment
	"""
	datoteke = []
	boxes = soup.findAll('div', { 'class' : 'box'} )
	for box in boxes:
		first_child = box.contents[0]
		title = first_child.string.rstrip('\n')
		if ("Datoteke" == title):
			for datoteka in box.findAll('div', {'class' : 'item'}):
				absolutize_url(datoteka.find('a'), 'href')
				for img in datoteka.findAll('img'):
					absolutize_url(img, 'src')				

				datoteke.append(datoteka)

	return datoteke

def absolutize_url(element, url_attribute):
	try:
		url = element[url_attribute]
		if not url.startswith('http://'):
			element[url_attribute] = "http://www.pf.uni-lj.si/" + url
	except KeyError:
		pass

def get_latest_novice_in_category(soup):
	""" return a list of maps, one per novice. keys are ["title", "date", "author", "url"]
	source sample:
<div class="list_item">
                                <span>03.03.2009 | Objavil: Milena Kastelic</span>
                                <h2 class="billboard"><span style="background-color: #ff0000;"></span><a href="/oglasna-deska/dodiplomski-studij-187/2.-letnik/kriminalistika-vpis-ocen-ogled-testov-6116/">Kriminalistika - vpis ocen, ogled testov</a></h2>
	"""
	novice_div_list = soup.findAll('div', { "class" : "list_item" })
	novice = []
	for novica_div in novice_div_list:
		meta = novica_div.span.contents[0]
		(date, author) = meta.split('|')
		date = date.strip()
		(d, m, y) = date.split('.')
		date = "%s-%s-%s" % (y,m,d)
		author = author.split(':')[1].strip()

		link = novica_div.h2.a
		title = link.contents[0]
		url  = link['href']

		novice.append({
			"title" : title,
			"date" : date,
			"author" : author,
			"url" : "http://www.pf.uni-lj.si" + url, 	
		})
	
	return novice

feeds = {
	u"1. letnik" : {
		"source": "http://www.pf.uni-lj.si/oglasna-deska/dodiplomski-studij-187/1.-letnik/?",
		"dest":		"http://vm04.kiberpipa.org/pf_rss/pf_1_letnik.xml",
		"file":		"pf_1_letnik.xml",
		"title":	"Oglasna deska za 1. letnik Pravne Fakultete Univerze v Ljubljani (neuradni rss)",
		"description": "Zadnjih 15 novic",
	},
	u"2. letnik" : {
		"source": "http://www.pf.uni-lj.si/oglasna-deska/dodiplomski-studij-187/2.-letnik/?",
		"dest":		"http://vm04.kiberpipa.org/pf_rss/pf_2_letnik.xml",
		"file":		"pf_2_letnik.xml",
		"title":	"Oglasna deska za 2. letnik Pravne Fakultete Univerze v Ljubljani (neuradni rss)",
		"description": "Zadnjih 15 novic",
	},		
	u"3. letnik" : {
		"source": "http://www.pf.uni-lj.si/oglasna-deska/dodiplomski-studij-187/3.-letnik/?",
		"dest":		"http://vm04.kiberpipa.org/pf_rss/pf_3_letnik.xml",
		"file":		"pf_3_letnik.xml",
		"title":	"Oglasna deska za 3. letnik Pravne Fakultete Univerze v Ljubljani (neuradni rss)",
		"description": "Zadnjih 15 novic",
	},		
	u"4. letnik" : {
		"source": "http://www.pf.uni-lj.si/oglasna-deska/dodiplomski-studij-187/4.-letnik/?",
		"dest":		"http://vm04.kiberpipa.org/pf_rss/pf_4_letnik.xml",
		"file":		"pf_4_letnik.xml",
		"title":	"Oglasna deska za 4. letnik Pravne Fakultete Univerze v Ljubljani (neuradni rss)",
		"description": "Zadnjih 15 novic",
	},		
	u"absolventi" : {
		"source": "http://www.pf.uni-lj.si/oglasna-deska/dodiplomski-studij-187/absolventi/?",
		"dest":		"http://vm04.kiberpipa.org/pf_rss/pf_absolventi.xml",
		"file":		"pf_absolventi.xml",
		"title":	"Oglasna deska za absolvente Pravne Fakultete Univerze v Ljubljani (neuradni rss)",
		"description": "Zadnjih 15 novic",
	},		
}

def make_feed(name):
	html = urllib2.urlopen(feeds[name]['source'])
	novice = get_latest_novice_in_category(BeautifulSoup(html))
	html.close()

	items = []
	for novica in novice:
		novica_html = urllib2.urlopen(novica['url'])
 		content = get_novica_content(BeautifulSoup(novica_html))
		novica_html.close()

		items.append(
			PyRSS2Gen.RSSItem(
				title = novica['title'], 
				link = novica['url'], 
				description = content, 
				guid = PyRSS2Gen.Guid(novica['title']), 
				pubDate = novica['date']
			)
		)

	
	image = PyRSS2Gen.Image( 
		"http://www.pf.uni-lj.si/images/pravna_logo_transparent.png", 
		feeds[name]['title'], 
		feeds[name]['dest'], 
	)

	# generate rss feed
	PyRSS2Gen.RSS2(
		title         = feeds[name]['title'],
		link          = feeds[name]['dest'],
	  description   = feeds[name]['description'],
		lastBuildDate = datetime.datetime.now(),
		image					= image,
    items         = items,
		webMaster			= u"ike@kiberpipa.org"
	).write_xml(open(feeds[name]['file'], "w"))
	print "Feed written to %s" % (feeds[name]['file'])

make_feed(sys.argv[1])
