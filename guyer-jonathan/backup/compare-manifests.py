import csv

def read_manifest(manifest_file):
    manifest = {}
    with open(manifest_file, mode="r") as csvfile:
        manifest_reader = csv.reader(csvfile, delimiter=",")
        for filehash, filename in manifest_reader:
            manifest[filehash] = filename

    return manifest

def compare_manifests(fileA, fileB):
    manifestA = read_manifest(fileA)
    manifestB = read_manifest(fileB)
    reversedA = {}
    reversedB = {}
    
    status = {
        "changed": {},
        "unchanged": {},
        "renamed": {},
        "deleted": {},
        "added": {}
    }
    
    for filehashA, filenameA in manifestA.items():
        if filehashA in manifestB:
            filenameB = manifestB.pop(filehashA)
            if filenameB == filenameA:
                status["unchanged"][filehashA] = filenameA
            else:
                status["renamed"][filehashA] = [filenameA, filenameB]
        else:
            # not found, so set up for reverse lookup
            reversedA[filenameA] = filehashA

    for filehashB, filenameB in manifestB.items():
        if filenameB in reversedA:
            filehashA = reversedA.pop(filenameB)
            status["changed"][filenameB] = [filehashA, filehashB]
        else:
            # not found, so set up for reverse lookup
            reversedB[filenameB] = filehashB
            
    # anything not removed from reversedA must have been deleted
    for filenameA, filehashA in reversedA.items():
        status["deleted"][filehashA] = filenameA
            
    # anything not removed from reversedB must have been added
    for filenameB, filehashB in reversedB.items():
        status["added"][filehashB] = filenameB

    return status

def test_read():
    manifest = read_manifest("test/manifestA.csv")

    expected = {
        'deadbeef': 'path/to/t-bone.txt',
        'cafeb0ba': 'path/to/boba/are_gross.txt',
        'decafbad': 'path/to/caffeine.py',
        '8badf00d': 'path/to/do/not/feel/good.py',
        'deadc0de': 'path/to/do/not/use.py'
    }

    assert manifest == expected

def test_compare():
    status = compare_manifests("test/manifestA.csv", "test/manifestB.csv")
    
    expected = {
        "changed": {"path/to/caffeine.py": ["decafbad", "c0ffeeee"]},
        "unchanged": {"deadc0de": "path/to/do/not/use.py"},
        "renamed": {"deadbeef": ["path/to/t-bone.txt", "path/to/porterhouse.txt"],
                    "cafeb0ba": ["path/to/boba/are_gross.txt", "path/to/boba/are_yum.txt"]},
        "deleted": {"8badf00d": "path/to/do/not/feel/good.py"},
        "added": {"bbadbeef": "path/to/smells/bad.csv"}
    }

    assert status == expected

def run_tests():
    skipped = []
    passed = []
    failed = []
    errored = []

    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        if hasattr(test, "skip"):
            print(f"skip: {name}")
            skipped.append(name)
            continue
        try:
            test()
            print(f"pass: {name}")
            passed.append(name)
        except AssertionError as e:
            print("docstring:", test.__doc__)
            if test.__doc__ == "test:assert":
                print(f"pass: {name}")
                passed.append(name)
            elif hasattr(test, "fail"):
                print(f"pass (expected failure): {name}")
                passed.append(name)
            else:
                print(f"fail: {name} {str(e)}")
                failed.append(name)
        except Exception as e:
            print(f"error: {name} {str(e)}")
            errored.append(name)

    print(f"{len(skipped)} tests skipped: {skipped}")
    print(f"{len(passed)} tests passed: {passed}")
    print(f"{len(failed)} tests failed: {failed}")
    print(f"{len(errored)} tests errored: {errored}")

    return skipped, passed, failed, errored

if __name__ == "__main__":
    run_tests()
