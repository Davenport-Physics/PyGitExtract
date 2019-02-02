from git import Repo
from datetime import datetime
import sys
import time

def main(argv):

    ParseArgv(argv)
    

def ParseArgv(argv):

    func_dict = {"-since": SinceArgv}
    for i in range(len(argv)):
        try:
            func_dict[argv[i]](argv, i)
        except KeyError:
            pass

def GetSecondaryCommand(argv, command, default):

    for i in range(len(argv)):
        if argv[i] == command:
            try:
                return argv[i+1]
            except:
                print("Passed " + command + " command, but no data given")
                sys.exit(0)

    return default

def GetUntilArgv(argv):

    for i in range(len(argv)):
        if argv[i] == "-until":
            try:
                return ConvertUserDate(argv[i+1] + " " + argv[i+2] + " " + argv[i+3])
            except:
                print("No good until date.")
                sys.exit(0)

    return ConvertEpochDate(time.time())

def GetDirIfPossible(argv):
    return None


def SinceArgv(argv, i):

    if len(argv[i:]) < 3:
        print("No good since date")
        sys.exit(0)

    date       = ConvertUserDate(argv[i+1] + " " + argv[i+2] + " " + argv[i+3])
    directory  = GetSecondaryCommand(argv, "-dir", "resources")
    count      = int(GetSecondaryCommand(argv, "-count", 1000))
    until_date = GetUntilArgv(argv)

    BeginWritingToFile(CommitObjectsUntil(CommitObjectsSince(GetCommitObjects(directory = directory, count = count), date), until_date))


def GetCommitObjects(directory = "resources", count = 1000):

    try:
        return list(Repo(directory).iter_commits('master', max_count=count))
    except:
        print("Directory never specificed or default not found.")
        sys.exit(0)

def CommitObjectsSince(commits, since_date):

    return DiluteCommitObjectsSince(commits, GetNormalTimeFromEpochTime(commits), since_date)

def CommitObjectsUntil(commits, until_date):

    return DiluteCommitObjectsUntil(commits, GetNormalTimeFromEpochTime(commits), until_date)

def ConvertUserDate(since_date):

    dates = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    relevant_date = since_date.split(' ')
    relevant_date[1] = dates[relevant_date[1]]

    return list(map(int, relevant_date))

def ConvertEpochDate(epoch_date):

    normal_time = str(datetime.fromtimestamp(epoch_date))
    normal_time = normal_time.split(" ")[0].split("-")
    normal_time.reverse()
    normal_time = list(map(int, normal_time))

    return normal_time

def GetNormalTimeFromEpochTime(commits):

    normal_times = []
    for commit in commits:
        normal_times.append(ConvertEpochDate(commit.authored_date))
    return normal_times

def DiluteCommitObjectsSince(commits, normal_times, since_date):

    return commits[:DateSinceComparison(normal_times, since_date, 0, [len(normal_times)])]

def DiluteCommitObjectsUntil(commits, normal_times, until_date):

    return commits[DateUntilComparison(normal_times, until_date, 2, -1):]

def DateSinceComparison(normal_times, since_date, comp_idx, end):

    if comp_idx > 2:
        return min(end)

    for i in range(len(normal_times)):
        if normal_times[i][comp_idx] < since_date[comp_idx]:
            if comp_idx != 2 and normal_times[i][comp_idx+1] > since_date[comp_idx+1]:
                continue
            end.append(i)
            return DateSinceComparison(normal_times, since_date, comp_idx + 1, end)

    return DateSinceComparison(normal_times, since_date, comp_idx + 1, end)

def DateUntilComparison(normal_times, until_date, comp_idx, start):

    if comp_idx < 0:
        return start+1

    for i in range(len(normal_times)-1, 0, -1):

        if normal_times[i][comp_idx] > until_date[comp_idx]:
            if comp_idx != 2 and normal_times[i][comp_idx+1] < until_date[comp_idx+1]:
                continue
            elif comp_idx == 0 and normal_times[i][1] > until_date[1] and normal_times[i][2] < until_date[2]:
                continue
            return DateUntilComparison(normal_times, until_date, comp_idx - 1, i)

    return DateUntilComparison(normal_times, until_date, comp_idx - 1, start)


def BeginWritingToFile(commits):

    WriteGitData(commits)
    WriteMiscData(commits)


def WriteGitData(commits):

    print("Writing Git Data cvs")
    fp = open("GitData.cvs", "w+")
    fp.write("insertions,deletions,lines,files,author_name,authored_date\n")
    for commit in commits:
        fp.write("%s,%s,%s,%s," % (commit.stats.total["insertions"], commit.stats.total["deletions"], commit.stats.total["lines"], commit.stats.total["files"]))
        fp.write("%s,%s\n" % (commit.author.name, str(datetime.fromtimestamp(commit.authored_date)).split(" ")[0]))
    fp.close()

def WriteMiscData(commits):

    print("Writing Git Misc Data cvs")
    fp = open("GitMiscData.cvs", "w+")
    fp.write("author,total_commits,insertions,deletions\n")

    authors               = GetAllUniqueAuthors(commits)
    commits_per_author    = CountCommitsPerAuthor(commits, authors)
    insertions_per_author = CountLOCChagesPerAuthor(commits, authors, "insertions")
    deletions_per_author  = CountLOCChagesPerAuthor(commits, authors, "deletions")
    for i in range(len(authors)):
        fp.write("%s,%d,%d,%d\n" % (authors[i], commits_per_author[i], insertions_per_author[i], deletions_per_author[i]))

    fp.close()

def GetAllUniqueAuthors(commits):

    authors = []
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
    for i in range(len(authors)):

        commits_per_author.append(0)
        for commit in commits:
            if commit.author.name == authors[i]:
                commits_per_author[i] += 1

    return commits_per_author

def CountLOCChagesPerAuthor(commits, authors, loc_type):

    locs = []
    for i in range(len(authors)):

        locs.append(0)
        for commit in commits:
            if commit.author.name == authors[i]:
                locs[i] += commit.stats.total[loc_type]

    return locs


main(sys.argv)