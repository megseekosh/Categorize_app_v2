'''
    shuffle_trial is a set of functions used to shuffle a set of labeled files
    into order by counting the number of repeated fields in each file (see
    comment documentation on the generate_repeats function)

    Max Scribner
    December 13, 2018
'''

DEBUG = False

''' This generates all valid arrays in the form
        [x_1, x_2, x_3 ... x_n] where x_i is an integer such that
                                      0 <= x_i < sizes[i]

    This is used to generate dummy files for the generate_repeats function
'''
def permute(sizes):
    all = []
    for i in range(sizes[0]):
        if len(sizes) > 1:
            for j in permute(sizes[1:]):
                all.append([i]+j)
        else:
            all.append([i])
    return all

'''
    This generates all valid shufflings of the elements parameter where a valid
    shuffling does not have more than (repeats[i]) elements consecutively with
    field i equal to the same value for every field i.

    This is easily used to shuffle a list of objects such that one property does
    not appear too many times in a row.


    The parameter elements is an array of elements to shuffle, each element
    formatted as an array of fields (int, string, mixed, etc.) used to
    represent properties of the object

    The parameter repeats is an array of integers representing the number of
    times the field with equivalent index can repeat in the shuffled output.
    If the value at an index of repeats is less than or equal to 0 then
    there is no bound on that associated field
'''
def generate_repeats(elements, repeats):
    outputs = []
    if len(elements) > 1:
        #Loop through all the possible values for this element
        for element_index in range(len(elements)):
                #Get all possible valid sequences which don't contain this value
                # represented in the form [ [value,], ]
                all_next = generate_repeats(elements[:element_index]+elements[element_index+1:],
                                            repeats)

                #For debugging. WARNING: Use only on small input values
                if DEBUG:
                    print ("Elements %s"%(elements))
                    print ("Element %s"%(values[element_index]))
                    print ("All next %s"%(all_next))
                    print "\n"

                #For each possible next sequence
                # check if this addition is valid
                for next in all_next:
                    #Ensure that this element does not cause an invalid repeat
                    # and if so, add it to the output

                    #Go through each label in the current element
                    for label_index in range(len(elements[element_index])):
                        valid_label = False
                        #if it's not even long enough to be invalid
                        if len(next) < repeats[label_index] or repeats[label_index] <= 0:
                            #Add concatenated version to the outputs
                            valid_label = True
                        else:
                            for count in range(repeats[label_index]):
                                #If one of the next REPEAT elements is not the
                                # repeat value, then REPEAT repeats has not
                                # occurred
                                #
                                # where REPEAT = the max number of repeats for the
                                # current symbol
                                valid_label |= next[count][label_index] != elements[element_index][label_index]

                        if not valid_label:
                            break;
                    else: # If all labels were valid
                        outputs.append([elements[element_index]]+next)
    else:#base case
        outputs.append([elements[0]])

    return outputs

if __name__ == "__main__":
    mutations = permute([2,3])
    print "\nMUTATIONS: %s"%mutations
    reps = generate_repeats(mutations, [1, 1])
    print "\nREPS:"
    for index in range(len(reps)):
        # This is complicated but suffice to say it prints out the list in a nice way
        print("Rep %d: \n\t%s"%(index+1, "\n\t".join([", ".join([str(y) for y in x]) for x in reps[index]])))
        print "\n"
