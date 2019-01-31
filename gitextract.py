from git import Repo
from datetime import datetime

def main():

    BeginWritingToFile(CommitObjectsSince(GetCommitObjects(count = 1000), "1 Jan 2019"))

def GetCommitObjects(directory = "resources", count = 50):

    return list(Repo(directory).iter_commits('master', max_count=count))

def CommitObjectsSince(commits, since_date):

    return DiluteCommitObjects(commits, GetNormalTimeFromEpochTime(commits), ConvertSinceDate(since_date))

def ConvertSinceDate(since_date):

    dates = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    relevant_date = since_date.split(' ')
    relevant_date[1] = dates[relevant_date[1]]

    return list(map(int, relevant_date))

def GetNormalTimeFromEpochTime(commits):

    normal_times = []
    for commit in commits:
        normal_time = str(datetime.fromtimestamp(commit.authored_date))
        normal_time = normal_time.split(" ")[0].split("-")
        normal_time.reverse()
        normal_times.append(list(map(int, normal_time)))
    return normal_times

def DiluteCommitObjects(commits, normal_times, since_date):

    return commits[:DateComparison(normal_times, since_date, 2, len(normal_times))]

def DateComparison(normal_times, since_date, comp_idx, end):

    if comp_idx < 0:
        return end

    for i in range(end):
        if normal_times[i][comp_idx] < since_date[comp_idx]:
            return DateComparison(normal_times, since_date, comp_idx - 1, i)

    return DateComparison(normal_times, since_date, comp_idx - 1, end)

def BeginWritingToFile(commits):

    WriteGitData(commits)
    WriteMiscData(commits)


def WriteGitData(commits):

    fp = open("GitData.cvs", "w+")
    fp.write("insertions,deletions,lines,files,author_name,authored_date\n")
    for commit in commits:
        fp.write("%s,%s,%s,%s," % (commit.stats.total["insertions"], commit.stats.total["deletions"], commit.stats.total["lines"], commit.stats.total["files"]))
        fp.write("%s,%s\n" % (commit.author.name, str(datetime.fromtimestamp(commit.authored_date))))
    fp.close()

def WriteMiscData(commits):

    fp = open("GitMiscData.cvs", "w+")
    fp.write("author, total_commits\n")

    authors = GetAllUniqueAuthors(commits)
    commits_per_authors = CountCommitsPerAuthor(commits, authors)
    for i in range(len(authors)):
        fp.write("%s,%d\n" % (authors[i], commits_per_author[i]))

    fp.close()

def GetAllUniqueAuthors(commits):

    authors = [commits[0].author.name]
    for commit in commits:

        found_duplicate = False
        for author in authors:

            if commit.author.name != author:
                continue
            else:
                found_duplicate = True
                break

        if found_duplicate == False:
            authors.append(commit.author.name)

    return authors

def CountCommitsPerAuthor(commits, authors):

    commits_per_author = []
    for i in range(len(author)):

        commits_per_author.append(0)
        for commit in commits:
            if commit.author.name == author[i]:
                commits_per_author[i] += 1

    return commits_per_author

main()