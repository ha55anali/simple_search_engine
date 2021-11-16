import click
import os
from nltk.stem import PorterStemmer
from collections import defaultdict


@click.group()
def main():
    """
    Simple CLI for making use of inverted indexes
    """
    pass


@main.command()
@click.argument('doc')
def search_doc(doc):
    """This search returns document related stats"""
    found = False
    total_count = 0

    for key in doc_dict:
        if key == doc:
            doc_id = doc_dict[key]["id"]
            for d in doc_index_dict:
                if d == doc_id:
                    click.echo("DOCID: " + doc_id)
                    click.echo('Distinct terms: ' + str(len(doc_index_dict[doc_id])))
                    for i in doc_index_dict[doc_id]:
                        total_count += int(i['term_count'])
                    found = True
            click.echo('Total terms: ' + str(total_count))
    if not found:
        click.echo("Document not found")


@main.command()
@click.argument('term')
def search_term(term):
    """This search returns document related stats for a term"""
    ps=PorterStemmer()
    term=ps.stem(term)
    found = False
    for key in term_dict:
        if key == term:
            click.echo("Listing for term: " + key)
            term_id = term_dict[key]["id"]
            click.echo("TERMID: " + term_id)
            click.echo("Number of documents containing term: " + term_info_dict[term_id]["d_count"])
            click.echo("Term frequency in corpus: " + term_info_dict[term_id]["o_count"])
            click.echo("Inverted list offset: " + term_info_dict[term_id]["offset"])
            found = True
    if not found:
        click.echo("Term not found")


@main.command()
@click.argument('term')
@click.argument('doc')
def search_term_wrt_doc(term, doc):
    """This search returns term stats wrt a certain doc"""
    found = False
    offset = 0
    doc_id = ''

    for key in term_dict:
        if key == term:
            for d in doc_dict:
                if d == doc:
                    click.echo("Inverted list for term: " + key)
                    click.echo("In document: " + doc)
                    term_id = term_dict[key]["id"]
                    click.echo("TERMID: " + term_id)
                    doc_id = doc_dict[d]["id"]
                    click.echo("DOCID: " + doc_id)
                    offset = int(term_info_dict[term_id]["offset"])
                    found = True
                    print(f'Found with id {term_id}')

    if not found:
        click.echo("Term not found")

    with open('term_index.txt', 'r') as f:
        f.seek(int(offset))
        line = f.readline().strip().split('\t')
        line = [x for x in line[1:] if x != '']
        for l in line:
            if l.split(':')[0] == doc_id:
                click.echo('Term frequency in document: ' + l.split(':')[1])
    f.close()


if __name__ == "__main__":
    # Using readlines()
    file = open('termids.txt', 'r')
    Lines = file.readlines()
    term_dict = {}
    term_info_dict = {}
    doc_dict = {}
    doc_index_dict = defaultdict(list)

    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        term_id, term = line.strip().split('\t')
        term_dict[term] = {'id': term_id}
    file.close()

    # Using readlines()
    file = open('term_info.txt', 'r')
    Lines = file.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        term_id, offset, o_count, d_count = line.strip().split('\t')
        term_info_dict[term_id] = {'offset': offset, 'o_count': o_count, 'd_count': d_count}
    file.close()

    # Using readlines()
    file = open('docids.txt', 'r')
    Lines = file.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        doc_id, doc = line.strip().split('\t')
        doc=os.path.basename(doc)
        doc_dict[doc] = {'id': doc_id}
    file.close()

    # Using readlines()
    file = open('forwardindex.txt', 'r')
    Lines = file.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
            content = line.strip().split('\t')
            if line.strip() != '':
                count += 1
                doc_id, term_id, term_count = content
                doc_index_dict[doc_id].append({'term_id': term_id, 'term_count': term_count})
    file.close()


    #print(doc_dict)
    main()
