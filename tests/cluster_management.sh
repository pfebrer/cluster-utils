
describe "Cluster management"
	clusters_yaml=$(clusterutils path clusters.yaml)
	describe "Listing"
		it "Works with no clusters.yaml"
			if [ -f "${clusters_yaml}" ]; then rm "${clusters_yaml}"; fi
			assert equal "$(clusterutils lsclusters)" ""
		end

		it "Finds clusters in clusters.yaml"
			# Populate the clusters.yaml manually
			printf "cl1:\n  whatever: yes\ncl2:\n  attribute: 2\n\ncl3:" > "${clusters_yaml}"
			assert equal "$(clusterutils lsclusters)" "cl1 cl2 cl3"
			rm "${clusters_yaml}"
		end
	end

	describe "Setup and removal"
		it "Sets up clusters from multiple yaml"
			printf "cl4:\n  user:person\n  hostname:whaat\n" > "${clusters_yaml}test1"
			printf "cl5:\n  user:person\n  hostname:other\n\ncl6:\n  user: person\n  hostname:hpc" > "${clusters_yaml}test2"
			clusterutils setupcluster "${clusters_yaml}test?" >/dev/null 2>/dev/null
			rm ${clusters_yaml}test?
			assert equal "$(clusterutils lsclusters)" "cl4 cl5 cl6"
		end

		it "Removes one cluster succesfully"
			clusterutils removecluster cl5
			assert equal "$(clusterutils lsclusters)" "cl4 cl6"
		end

		it "Removes all clusters succesfully"
			clusterutils removecluster --all
			assert equal "$(clusterutils lsclusters)" ""
		end
	end

	describe "Listing mounts"
		
		it "Works with no mounts directory"
			assert equal "$(clusterutils lsmounts)" ""
		end

		it "Lists mountpoints correctly"
			test_lsmount(){
				# Create some fake mountpoints
				mkdir -p "${CLUSTER_UTILS_MOUNTS}/test1" "${CLUSTER_UTILS_MOUNTS}/test2" 
				assert equal "$(clusterutils lsmounts)" "test1 test2"
				# Remove all of them very safely
				rmdir "${CLUSTER_UTILS_MOUNTS}/test1" "${CLUSTER_UTILS_MOUNTS}/test2" "${CLUSTER_UTILS_MOUNTS}"
			}
			test_lsmount
		end
		
		it "Works with mounts dir other than default"
			CLUSTER_UTILS_MOUNTS=$(clusterutils path othermounts) test_lsmount
		end	
	end
end
