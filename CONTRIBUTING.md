# Contributing to ix.ai/crypto-exporter

Community contributions are welcome and help move the project along.  Please review this document before sending any merge requests.

Thanks!

## TL;DR

* Fork the repository on [GitLab](https://gitlab.com/ix.ai/crypto-exporter)!
* Create a topic branch in your forked repository, based on the master branch
* Submit a [Merge Request](https://gitlab.com/ix.ai/crypto-exporter/-/merge_requests)

## GitLab Project

This project is hosted on [gitlab.com](https://gitlab.com/ix.ai/crypto-exporter). Contributions are accepted only with merge requests on GitLab!

## Existing Functionality and Breaking Changes

As a rule, merge requests that break existing functionalities are rejected. Feel free to challenge it, though.

## Bug Fixes

All bug fixes are welcome. Please try to add a test if the bug is something that should have been fixed already. Oops.

## Feature Additions

New features are welcome provided that the feature has a general audience and is reasonably simple.  The goal of the repository is to support a wide audience and be simple enough.

Please add new documentation in the `docs` folder for any new features.  Merge requests for missing documentation are always welcomed. Keep the `README.md` focused on the most popular use cases, details belong in the docs directory.

If you want to implement a special feature, it will likely be accepted assuming you add the tests and follow the style guidelines below.

## Style

The style of the repo follows that of the Linux kernel, in particular:

* Merge requests should be rebased to small atomic commits so that the merged history is more coherent
* The subject of the commit should be in the form "`<subsystem>: <subject>`" or "`<issue_number># <subsystem>: <subject>`"
* More details in the body
* Match surrounding coding style (line wrapping, spaces, etc)

More details in the [SubmittingPatches](https://www.kernel.org/doc/html/latest/process/submitting-patches.html) document included with the Linux kernel.  In particular the following sections:

* `2) Describe your changes`
* `3) Separate your changes`
