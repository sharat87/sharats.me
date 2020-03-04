---
title: Dependency Injection In Python
tags: [python, python-importlib, python-inspect, reflection]
description: >
    A write-up of a simple implementation of dependency injection (DI) in Python using only the
    standard library's importlib and inspect modules.
---

I chose a form of dependency injection (DI) as the solution to a recent problem I needed to solve.
This is a quick write-up of how I did it in Python, using the standard library modules.

[TOC]

## The Problem

I'll be illustrating the problem in a slightly different context so as to not reveal too many
details of the subject matter. So, if the problem feels unrealistic or stupid, that's just a result
of my unimaginative thinking.

We have an application, let's call it the task runner, that lets users choose a task to run, and
runs that task. Each such task is implemented as a separate Python script file, that take no user
inputs, but do connect to a database and a few REST endpoints.

So this is how it works. We have a bunch of wrapper classes that provide high-level abstractions for
the database and the REST endpoints. Instances of these classes are given to the task scripts, which
use them to perform the their task.

The task scripts are also expected to *return* some information back to our application, with
details such as whether the task was successful or the reasons if there's an error etc. The approach
for how this is done is detailed in the following Solution section(s).

## The Legacy Solution

The current way this is working (which I took the liberty to call *The Legacy Solution*) is that
when a user requests for a specific task to be run, the application reads up the relevant Python
script file and calls `eval` on the contents. A pre-made dictionary holding all the instances of
high-level abstractions is provided in the global scope of this call to `eval`.

This has been working well for several years now and, although it feels dirty in hindsight, there
were probably good reasons it was done this way:

1. It was very simple and easy to implement. There's little to no magic.
1. The task scripts can be updated on production without restarting the application and the changes
   would take affect immediately.
1. The scripts' logic can be written as module level code. Full freedom on how the code is
   structured and written.

Arguing on how horrible this approach is would be a great topic for a heated debate, and,
fortunately that's not what I set to write about here. For reasons I won't go into, we decided to
move to a more sophisticated approach and so started looking.

A major reason (among several) for this decision was to have the scripts not depend on implicit
globals. The use of implicit globals meant that the scripts were using variables that appear as not
defined to static code analyzers.  Additionally, since the script file was being read into a string
and `eval`-ed, the stack trace from any errors were not very helpful.

## The New DI Solution

In the new proposed way for this to work, we have made three critical changes:

1. The Python script files will be `import`-ed as Python modules, and the `task_main` function at
   the module level will be called to run the task.
1. Nothing is implicitly injected into the script's global scope.
1. Access to the API abstractions is done through a form of dependency injection.

In the task scripts, we have a function defined like the following:

    :::python
    def task_main(users_service, sales_service):
        # do something with `users_service` and `sales_service`.

Here, the `task_main` function is defined to accept two arguments. The `users_service` and
`sales_service`. In our task runner application, we use the `inspect` module to identify the
abstractions being used in `task_main` and pass them accordingly. Here's how it works:

    :::python {linenos: true}
    import importlib
    import inspect

    def run_task_script(script):
        module_name = script.replace('.py', '')
        module = importlib.import_module(module_name)
        args = inspect.signature(module.task_main).parameters

        kwargs = {}

        for name in args:
            kwargs[name] = get_service_instance(name)

        response = module.task_main(**kwargs)

        record_task_response(response)

In this function, we first convert the script file name into it's module name (hoping it doesn't
contain any spaces or dash characters). Then, we use the `importlib` module to import the module of
that name. Next, we call `inspect.signature` function on the module's `task_main` function to get
it's parameter names.

Based on these argument names (in `args`), we then construct a dictionary with these names as keys
and the instance of the API abstraction class, as the value. We then pass this as the keyword
arguments to the call to `module.task_main`.

In this way, the scripts don't assume any implicit globals and the `task_main` accepts arguments
that it needs and no more. This makes the code much cleaner and easier to do static analysis on.
Besides, since we import the module and call a function in it, we get nicer stack traces when
there's an exception.

## Conclusion

I'm sure there's better, and more involved implementations of doing DI in Python, but what we've
done above is enough for the target problem. Additionally, it's just using the standard library, so,
extra brownie points for that!
